#Importaciones de dependencias de Django
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from proyectos.serializers.proyecto_serializer import ParticipacionSerializer
from rest_framework.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode

from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator



#Importaciones internas de los módulos
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.rol import Rol
from usuarios.models.usuario import Usuario

from proyectos.serializers.participacion_serializer import ParticipacionDetalleSerializer
from proyectos.serializers.proyecto_serializer import (
    ProyectoSerializer,
    InvitacionColaboradorSerializer,
    CambiarRolSerializer,
    ProyectoConParticipacionSerializer
)

#Gestión de operaciones CRUD(create, read, update, delete) Y lógica personalizada de manipulación de proyectos
class ProyectoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProyectoSerializer  
    
    def get_queryset(self):
        user = self.request.user
        proyectos_ids = Participacion.objects.filter(
            id_usuario=user
        ).values_list('id_proyecto', flat=True)
        return Proyecto.objects.filter(id_proyecto__in=proyectos_ids)

    # 🔸 Vista personalizada para obtener un proyecto con todos sus participantes
    @action(detail=True, methods=['get'], url_path='con-participaciones')
    def con_participaciones(self, request, pk=None):
        try:
            proyecto = Proyecto.objects.get(pk=pk)
        except Proyecto.DoesNotExist:
            return Response({'detail': 'No Proyecto matches the given query.'}, status=status.HTTP_404_NOT_FOUND)

        participaciones = Participacion.objects.filter(id_proyecto=proyecto)
        serializer = ParticipacionSerializer(participaciones, many=True)
        return Response(serializer.data)

    #Al crear un proyecto, el usuario creador pasa a ser PMO, y se crean dos user inactivos Scrum Master y Developer
    def perform_create(self, serializer):
        usuario_actual = Usuario.objects.get(id=self.request.user.id)
        proyecto = serializer.save(usuario=usuario_actual)

        # Buscar roles ya existentes, lanzar error si no están
        try:
            rol_pmo = Rol.objects.get(nombre_rol='project_management')
            rol_sm = Rol.objects.get(nombre_rol='scrum_master')
            rol_dev = Rol.objects.get(nombre_rol='developer')
        except Rol.DoesNotExist as e:
            raise ValidationError(f"Rol requerido no definido en la base de datos: {str(e)}")

        # Crear participación del creador como Project Manager
        Participacion.objects.create(
            id_usuario=usuario_actual,
            id_proyecto=proyecto,
            id_rol=rol_pmo,
            estado_participacion='activo'
        )

        # Crear slots vacíos para SM y Dev
        Participacion.objects.create(
            id_usuario=None,
            id_proyecto=proyecto,
            id_rol=rol_sm,
            estado_participacion='inactivo'
        )

        Participacion.objects.create(
            id_usuario=None,
            id_proyecto=proyecto,
            id_rol=rol_dev,
            estado_participacion='inactivo'
        )
        #Actualización de proyectos
    def perform_update(self, serializer):
        proyecto_actualizado = serializer.save()

        print("Validando roles para cerrar proyecto...")
        print("Estado:", proyecto_actualizado.estado_proyecto)

        # Si no se está cerrando (finalizando), no se valida nada especial
        if proyecto_actualizado.estado_proyecto != "finalizado":
            return

        usuario_actual = self.request.user

        # Validar que el usuario participa en el proyecto
        try:
            participacion_usuario = Participacion.objects.get(
                id_usuario=usuario_actual,
                id_proyecto=proyecto_actualizado,
                estado_participacion="activo"
            )
        except Participacion.DoesNotExist:
            raise ValidationError("No puedes cerrar el proyecto si no participas en él.")

        # Validar que su rol sea PMO
        if participacion_usuario.id_rol.nombre_rol != "project_management":
            raise ValidationError("Solo el Project Management (PMO) puede cerrar el proyecto.")

        # Validar existencia de Scrum Master
        tiene_scrum_master = Participacion.objects.filter(
            id_proyecto=proyecto_actualizado,
            id_rol__nombre_rol="scrum_master",
            id_usuario__isnull=False,
            estado_participacion="activo"
        ).exists()

        # Validar existencia de Developer
        tiene_developer = Participacion.objects.filter(
            id_proyecto=proyecto_actualizado,
            id_rol__nombre_rol="developer",
            id_usuario__isnull=False,
            estado_participacion="activo"
        ).exists()

        if not (tiene_scrum_master and tiene_developer):
            raise ValidationError(
                "No puedes cerrar el proyecto sin un Scrum Master y al menos un Developer activos asignados."
            )

    #Obtener estadisticas de los proyectos asociados al usuario
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        user = request.user

        proyectos_ids = Participacion.objects.filter(id_usuario=user).values_list('id_proyecto', flat=True).distinct()
        queryset = Proyecto.objects.filter(id_proyecto__in=proyectos_ids)

        ultimo = queryset.last()

        # Obtener rol si hay último proyecto
        rol = None
        if ultimo:
            participacion = Participacion.objects.filter(id_usuario=user, id_proyecto=ultimo).first()
            rol = participacion.id_rol.nombre_rol if participacion else None

        return Response({
            'total_proyectos': queryset.count(),
            'proyectos_activos': queryset.filter(estado_proyecto='activo').count(),
            'proyectos_en_progreso': queryset.filter(estado_proyecto='en_progreso').count(),
            'proyectos_finalizados': queryset.filter(estado_proyecto='finalizado').count(),
            'ultimo_proyecto': {
                'id': ultimo.id_proyecto if ultimo else None,
                'nombre': ultimo.nombre if ultimo else None,
                'estado': ultimo.estado_proyecto if ultimo else None,
                'mi_rol': rol
            }
        })
# ════════════════════════════════════════════════════════════════════════
# 🚀  InvitarColaboradorView
# ════════════════════════════════════════════════════════════════════════
class InvitarColaboradorView(APIView):
    """
    Envía una invitación para colaborar en un proyecto:
      1) Si el usuario NO existe o está inactivo  → link completar‑registro
      2) Si el usuario ya existe y está activo    → link login + link aceptar‑invitación
    """

    def post(self, request, *args, **kwargs):
        # ----------------------------------------------------------------
        # Autenticación
        # ----------------------------------------------------------------
        jwt_authenticator = JWTAuthentication()
        auth_tuple = jwt_authenticator.authenticate(request)
        if auth_tuple is None:
            return Response({"error": "No autenticado"}, status=401)
        usuario_que_invita, _ = auth_tuple

        # ----------------------------------------------------------------
        # Validación de entrada
        # ----------------------------------------------------------------
        serializer = InvitacionColaboradorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email       = serializer.validated_data["email"]
        proyecto_id = serializer.validated_data["proyecto_id"]
        rol_id      = serializer.validated_data["rol_id"]

        # ----------------------------------------------------------------
        # Proyecto
        # ----------------------------------------------------------------
        try:
            proyecto = Proyecto.objects.get(id_proyecto=proyecto_id)
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado"}, status=404)

        # ----------------------------------------------------------------
        # Usuario invitado
        # ----------------------------------------------------------------
        usuario, creado = Usuario.objects.get_or_create(email=email)
        usuario_nuevo_o_inactivo = (creado or not usuario.is_active)

        if created := creado:
            usuario.is_active = False
            usuario.set_unusable_password()
            usuario.save()

        # ----------------------------------------------------------------
        # Rol
        # ----------------------------------------------------------------
        try:
            rol_asignado = Rol.objects.get(id_rol=rol_id)
        except Rol.DoesNotExist:
            return Response({"error": "Rol no válido"}, status=400)

        # Unicidad para Scrum Master / Project Management
        if rol_asignado.nombre_rol.lower() in ("scrum_master", "project_management"):
            existe_rol_exclusivo = Participacion.objects.filter(
                id_proyecto=proyecto,
                id_rol=rol_asignado,
                id_usuario__isnull=False
            ).exists()
            if existe_rol_exclusivo:
                return Response(
                    {"error": f"Ya existe un {rol_asignado.nombre_rol} en este proyecto"},
                    status=400
                )

        # Impedir que el usuario ya participe
        if Participacion.objects.filter(id_usuario=usuario, id_proyecto=proyecto).exists():
            return Response(
                {"error": f"El usuario {email} ya participa en este proyecto"},
                status=400
            )

        # ----------------------------------------------------------------
        # Participación (slot libre o nueva)
        # ----------------------------------------------------------------
        participacion = (
            Participacion.objects
            .filter(id_usuario=None, id_proyecto=proyecto, id_rol=rol_asignado)
            .first()
        )
        if participacion:
            participacion.id_usuario = usuario
            participacion.invitado_por = usuario_que_invita
            participacion.estado_participacion = "inactivo"
            participacion.save()
        else:
            participacion = Participacion.objects.create(
                id_usuario=usuario,
                id_proyecto=proyecto,
                id_rol=rol_asignado,
                estado_participacion="inactivo",
                invitado_por=usuario_que_invita
            )

        # ----------------------------------------------------------------
        # Enlaces según el caso
        # ----------------------------------------------------------------
        uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
        token  = default_token_generator.make_token(usuario)

        if usuario_nuevo_o_inactivo:
            # Completar registro
            url_registro = request.build_absolute_uri(
                reverse("completar-registro") + f"?uid={uidb64}&token={token}"
            )
            enlace_principal = url_registro
            texto_accion = "Completa tu registro"
        else:
            # Login y aceptar invitación
            url_login = request.build_absolute_uri(reverse("login"))
            url_aceptar = request.build_absolute_uri(
                reverse("aceptar-invitacion") +
                f"?participacion={participacion.id_participacion}&token={token}"
            )
            enlace_principal = (
                f"{url_login}\n\nDespués de iniciar sesión, confirma tu invitación aquí:\n👉 {url_aceptar}"
            )
            texto_accion = "Inicia sesión y acepta la invitación"

        # ----------------------------------------------------------------
        # Correo electrónico
        # ----------------------------------------------------------------
        mensaje_email = f"""
🌟 ¡Has sido invitado al proyecto *{proyecto.nombre}* como **{rol_asignado.nombre_rol.upper()}**!

Invitación enviada por: {usuario_que_invita.nombre_completo} ({usuario_que_invita.email})

🔗 {texto_accion}:
{enlace_principal}

Si no esperabas esta invitación, ignora este mensaje.

Saludos,
Taskly 🚀
"""
        send_mail(
            subject="🚀 Invitación a colaborar en un proyecto",
            message=mensaje_email,
            from_email="collabappdjango@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # ----------------------------------------------------------------
        # Respuesta JSON
        # ----------------------------------------------------------------
        return Response({
            "mensaje": "Invitación creada",
            "usuario": {
                "id": usuario.id,
                "email": usuario.email,
                "estado": "activo" if usuario.is_active else "inactivo"
            },
            "proyecto": {
                "id": proyecto.id_proyecto,
                "nombre": proyecto.nombre
            },
            "rol_asignado": {
                "id": rol_asignado.id_rol,
                "nombre_rol": rol_asignado.nombre_rol
            },
            "participacion": {
                "id": participacion.id_participacion,
                "estado_participacion": participacion.estado_participacion
            },
            "invitado_por": {
                "id": usuario_que_invita.id,
                "email": usuario_que_invita.email,
                "nombre_completo": usuario_que_invita.nombre_completo
            },
            "link_principal": enlace_principal
        }, status=status.HTTP_200_OK)


# ════════════════════════════════════════════════════════════════════════
# ✅  AceptarInvitacionView
# ════════════════════════════════════════════════════════════════════════
class AceptarInvitacionView(APIView):
    """
    Activa la participación cuando el usuario acepta la invitación
    mediante el enlace que recibió por correo.
    """

    def get(self, request, *args, **kwargs):
        participacion_id = request.query_params.get("participacion")
        token            = request.query_params.get("token")

        if not participacion_id or not token:
            return Response({"error": "Faltan parámetros"}, status=400)

        # Participación
        try:
            participacion = (
                Participacion.objects
                .select_related("id_usuario", "id_proyecto")
                .get(id_participacion=participacion_id)  # <- clave correcta
            )
        except Participacion.DoesNotExist:
            return Response({"error": "Participación no encontrada"}, status=404)

        usuario = participacion.id_usuario

        # Verificar token
        if not default_token_generator.check_token(usuario, token):
            return Response({"error": "Token inválido o expirado"}, status=400)

        # Activar participación
        participacion.estado_participacion = "activo"
        participacion.save()

        # Activar usuario si sigue inactivo
        if not usuario.is_active:
            usuario.is_active = True
            usuario.save()

        return Response({
            "mensaje": "Invitación aceptada con éxito",
            "usuario": {
                "id": usuario.id,
                "email": usuario.email,
                "estado": "activo"
            },
            "proyecto": {
                "id": participacion.id_proyecto.id_proyecto,
                "nombre": participacion.id_proyecto.nombre
            }
        }, status=200)

#Cambiar rol de un participante: solo puede hacerlo un PMO
class CambiarRolParticipanteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CambiarRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        id_usuario = serializer.validated_data["id_usuario"]
        id_proyecto = serializer.validated_data["id_proyecto"]
        nuevo_rol_clave = serializer.validated_data["nuevo_rol"]

        try:
            participacion = Participacion.objects.get(
                id_usuario=id_usuario,
                id_proyecto=id_proyecto
            )
        except Participacion.DoesNotExist:
            return Response({"error": "La participación no existe."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            nuevo_rol = Rol.objects.get(nombre_rol=nuevo_rol_clave)
        except Rol.DoesNotExist:
            return Response({"error": "Rol no válido."}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validar que el request.user sea PM del proyecto
        es_pm = Participacion.objects.filter(
            id_usuario=request.user,
            id_proyecto=id_proyecto,
            id_rol__nombre_rol='project management',
            estado_participacion='activo'
        ).exists()

        if not es_pm:
            return Response({"error": "Solo el Project Manager puede cambiar roles."},
                            status=status.HTTP_403_FORBIDDEN)

        if participacion.estado_participacion != "activo":
            return Response({"error": "Solo se puede cambiar el rol de una participación activa."},
                            status=status.HTTP_400_BAD_REQUEST)

        if nuevo_rol.nombre_rol == 'scrum_master':
            ya_hay_scrum_master = Participacion.objects.filter(
                id_proyecto=id_proyecto,
                id_rol__nombre_rol='scrum_master'
            ).exclude(id_participacion=participacion.id_participacion).exists()

            if ya_hay_scrum_master:
                return Response({"error": "Este proyecto ya tiene un Scrum Master asignado."},
                                status=status.HTTP_400_BAD_REQUEST)

        rol_anterior = serializer.validated_data["rol_anterior"]
        participacion.id_rol = nuevo_rol
        participacion.save()

        return Response({
            "mensaje": "Rol actualizado correctamente.",
            "rol_anterior": rol_anterior,
            "rol_nuevo": nuevo_rol.nombre_rol
        }, status=status.HTTP_200_OK)

#Prueba formulario básico de registro por invitación con método Post
@csrf_exempt
def completar_registro_view(request):
    uidb64 = request.GET.get("uid")
    token = request.GET.get("token")

    try:
        uid = urlsafe_base64_decode(uidb64).decode()  # ✅ decodificar
        user = Usuario.objects.get(id=uid)
    except (Usuario.DoesNotExist, ValueError, TypeError, OverflowError):
        return HttpResponse("Usuario no válido", status=400)

    if not default_token_generator.check_token(user, token):
        return HttpResponse("Token inválido o expirado", status=400)

    if request.method == "POST":
        password = request.POST.get("password")

        if not password:
            return HttpResponse("Debes ingresar una contraseña.", status=400)

        user.is_active = True
        user.password = make_password(password)
        user.save()

        Participacion.objects.filter(
            id_usuario=user, estado_participacion="inactivo"
        ).update(estado_participacion="activo")

        return HttpResponse("¡Tu cuenta ha sido activada! Ya puedes iniciar sesión.")

    return HttpResponse(f"""
        <h2>Completar Registro</h2>
        <form method="POST">
            <input type="hidden" name="uid" value="{uidb64}" />
            <input type="hidden" name="token" value="{token}" />
            <label>Ingresa tu nueva contraseña:</label><br>
            <input type="password" name="password" required/><br><br>
            <button type="submit">Activar cuenta</button>
        </form>
    """)