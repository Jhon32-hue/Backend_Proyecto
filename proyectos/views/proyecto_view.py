# Importaciones de dependencias de Django
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
from django.utils.encoding import force_str
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from rest_framework.permissions import AllowAny

# Importaciones internas de los módulos
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

# Gestión de operaciones CRUD(create, read, update, delete) y lógica personalizada de manipulación de proyectos
class ProyectoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProyectoSerializer  

    def get_queryset(self):
        user = self.request.user
        proyectos_ids = Participacion.objects.filter(
            id_usuario=user
        ).values_list('id_proyecto', flat=True)
        return Proyecto.objects.filter(id_proyecto__in=proyectos_ids)

    # Vista personalizada para obtener un proyecto con todos sus participantes
    @action(detail=True, methods=['get'], url_path='con-participaciones')
    def con_participaciones(self, request, pk=None):
        try:
            proyecto = Proyecto.objects.get(pk=pk)
        except Proyecto.DoesNotExist:
            return Response({'detail': 'No Proyecto matches the given query.'}, status=status.HTTP_404_NOT_FOUND)

        participaciones = Participacion.objects.filter(id_proyecto=proyecto)
        serializer = ParticipacionSerializer(participaciones, many=True)
        return Response(serializer.data)

    # Al crear un proyecto, el usuario creador pasa a ser PMO, y se crean dos user inactivos Scrum Master y Developer
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

    def perform_update(self, serializer):
        proyecto_actualizado = serializer.instance
        usuario_actual = self.request.user
        nuevo_estado = serializer.validated_data.get('estado_proyecto')

        # 🔐 Validación EXTRA: si el proyecto ya está cerrado, solo el PMO puede hacer cualquier modificación
        if proyecto_actualizado.estado_proyecto == 'finalizado':
            try:
                participacion_usuario = Participacion.objects.get(
                    id_usuario=usuario_actual,
                    id_proyecto=proyecto_actualizado,
                    estado_participacion="activo"
                )
            except Participacion.DoesNotExist:
                raise ValidationError("No puedes modificar un proyecto cerrado si no participas en él.")

            if participacion_usuario.id_rol.nombre_rol != "project_management":
                raise ValidationError("Solo el Project Management (PMO) puede modificar un proyecto cerrado.")

        # 🧩 Validación para cerrar el proyecto (cambiar el estado a "finalizado")
        if nuevo_estado == "finalizado":
            try:
                participacion_usuario = Participacion.objects.get(
                    id_usuario=usuario_actual,
                    id_proyecto=proyecto_actualizado,
                    estado_participacion="activo"
                )
            except Participacion.DoesNotExist:
                raise ValidationError("No puedes cerrar el proyecto si no participas en él.")

            if participacion_usuario.id_rol.nombre_rol != "project_management":
                raise ValidationError("Solo el Project Management (PMO) puede cerrar el proyecto.")

            tiene_scrum_master = Participacion.objects.filter(
                id_proyecto=proyecto_actualizado,
                id_rol__nombre_rol="scrum_master",
                id_usuario__isnull=False,
                estado_participacion="activo"
            ).exists()

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

            # ✔️ Si todo está validado y es cierre: forzamos el cambio y guardamos
            proyecto_actualizado.estado_proyecto = "finalizado"
            proyecto_actualizado.save()
            print(f"✅ Proyecto '{proyecto_actualizado.nombre}' cerrado exitosamente.")
            return

        # 🟢 Guardar normalmente si no es cierre
        serializer.save()


    # Obtener estadísticas de los proyectos asociados al usuario
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
    Envía una invitación :
        ─ Si el usuario YA está activo → sólo inicia sesión y la vista le activa la participación.
        ─ Si el usuario está inactivo/nuevo → la vista le pide completar registro y luego activa participación.
    """

    def post(self, request, *args, **kwargs):
        # ───── Autenticación
        jwt_authenticator = JWTAuthentication()
        auth_tuple = jwt_authenticator.authenticate(request)
        if auth_tuple is None:
            return Response({"error": "No autenticado"}, status=401)
        usuario_que_invita, _ = auth_tuple

        # ───── Validación de entrada
        s = InvitacionColaboradorSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        email       = s.validated_data["email"]
        proyecto_id = s.validated_data["proyecto_id"]
        rol_id      = s.validated_data["rol_id"]

        # ───── Proyecto y rol
        try:
            proyecto = Proyecto.objects.get(id_proyecto=proyecto_id)
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado"}, status=404)

        try:
            rol_asignado = Rol.objects.get(id_rol=rol_id)
        except Rol.DoesNotExist:
            return Response({"error": "Rol no válido"}, status=400)

        # ───── Usuario invitado
        usuario, creado = Usuario.objects.get_or_create(email=email)
        usuario_nuevo_o_inactivo = (creado or not usuario.is_active)
        if creado:
            usuario.is_active = False
            usuario.set_unusable_password()
            usuario.save()

        # ───── Unicidad de SM / PM
        if rol_asignado.nombre_rol.lower() in ("scrum_master", "project_management"):
            if Participacion.objects.filter(
                id_proyecto=proyecto, id_rol=rol_asignado, id_usuario__isnull=False
            ).exists():
                return Response(
                    {"error": f"Ya existe un {rol_asignado.nombre_rol} en este proyecto"},
                    status=400,
                )

        # ───── Evitar duplicados
        if Participacion.objects.filter(id_usuario=usuario, id_proyecto=proyecto).exists():
            return Response(
                {"error": f"El usuario {email} ya participa en este proyecto"},
                status=400,
            )

        # ───── Crear / asignar participación inactiva
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
                invitado_por=usuario_que_invita,
            )

        # ───── Construir enlace único
        uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
        token  = default_token_generator.make_token(usuario)

        FRONTEND_URL = "http://localhost:4200/verify-account"

        url_invitacion = f"{FRONTEND_URL}?participacion={participacion.id_participacion}&uid={uidb64}&token={token}"

        texto_accion = "Acepta tu invitación"


        # ───── Correo
        mensaje_email = f"""
🌟 ¡Has sido invitado al proyecto *{proyecto.nombre}* como **{rol_asignado.nombre_rol.upper()}**!

Invitación enviada por: {usuario_que_invita.nombre_completo} ({usuario_que_invita.email})

🔗 {texto_accion}:
{url_invitacion}

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

        return Response(
            {
                "mensaje": "Invitación creada",
                "link_principal": url_invitacion,
                "participacion": participacion.id_participacion,
            },
            status=status.HTTP_200_OK,
        )

class GestionInvitacionView(APIView):
    permission_classes = [AllowAny]
    """
    ✅ Maneja la aceptación de una invitación desde un solo enlace:
        - Si el usuario está activo → solo activa participación.
        - Si el usuario está inactivo → pide completar registro y activa participación.
    """

    def get(self, request, *args, **kwargs):
        uid         = request.query_params.get("uid")
        token       = request.query_params.get("token")
        particip_id = request.query_params.get("participacion")

        if not all([uid, token, particip_id]):
            return Response({"error": "Faltan parámetros"}, status=400)

        try:
            uid_int = force_str(urlsafe_base64_decode(uid))
            usuario = get_object_or_404(Usuario, pk=uid_int)
        except Exception:
            return Response({"error": "UID inválido"}, status=400)

        if not default_token_generator.check_token(usuario, token):
            return Response({"error": "Token inválido o expirado"}, status=400)

        participacion = get_object_or_404(Participacion, pk=particip_id, id_usuario=usuario)

        return Response({
            "usuario_activo": usuario.is_active,
            "usuario_email": usuario.email,
            "participacion_id": participacion.id_participacion,
            "proyecto_nombre": participacion.id_proyecto.nombre,
            "rol": participacion.id_rol.nombre_rol
        }, status=200)

    def post(self, request, *args, **kwargs):
        uid = request.query_params.get("uid")
        token = request.query_params.get("token")
        particip_id = request.query_params.get("participacion")

        if not all([uid, token, particip_id]):
            return Response({"error": "Faltan parámetros"}, status=400)

        try:
            uid_int = force_str(urlsafe_base64_decode(uid))
            usuario = get_object_or_404(Usuario, pk=uid_int)
        except Exception:
            return Response({"error": "UID inválido"}, status=400)

        if not default_token_generator.check_token(usuario, token):
            return Response({"error": "Token inválido o expirado"}, status=400)

        participacion = get_object_or_404(Participacion, pk=particip_id, id_usuario=usuario)

        # Si está inactivo, debe completar nombre y contraseña
        if not usuario.is_active:
            nombre = request.data.get("nombre_completo")
            password = request.data.get("password")

            if not nombre or not password:
                return Response({"error": "Nombre y contraseña requeridos"}, status=400)

            usuario.nombre_completo = nombre
            usuario.set_password(password)
            usuario.is_active = True
            usuario.save()

        # Activar participación
        participacion.estado_participacion = "activo"
        participacion.save()

        return Response({
            "mensaje": "Invitación aceptada con éxito",
            "usuario": {
                "id": usuario.id,
                "email": usuario.email,
                "nombre": usuario.nombre_completo,
                "estado": "activo"
            },
            "proyecto": {
                "id": participacion.id_proyecto.id_proyecto,
                "nombre": participacion.id_proyecto.nombre
            },
            "rol": participacion.id_rol.nombre_rol
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

