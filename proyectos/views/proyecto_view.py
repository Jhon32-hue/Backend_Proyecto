#Importaciones de dependencias de Django
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication

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

    #Listar proyectos asociados al usuario autenticado
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)
    
    # 🔸 Vista personalizada para obtener un proyecto con todos sus participantes
    @action(detail=True, methods=['get'], url_path='con-participaciones')
    def con_participaciones(self, request, pk=None):
        proyecto = self.get_object()
        serializer = ProyectoConParticipacionSerializer(proyecto)
        return Response(serializer.data)

    #Al crear un proyecto, el usuario creador pasa a ser PMO, y se crean dos user inactivos Scrum Master y Developer
    def perform_create(self, serializer):
        usuario_actual = Usuario.objects.get(id=self.request.user.id)
        proyecto = serializer.save(usuario=usuario_actual)

        rol_pmo, _ = Rol.objects.get_or_create(nombre_rol='project management')
        rol_sm, _ = Rol.objects.get_or_create(nombre_rol='scrum_master')
        rol_dev, _ = Rol.objects.get_or_create(nombre_rol='developer')

        Participacion.objects.create(
            id_usuario=usuario_actual,
            id_proyecto=proyecto,
            id_rol=rol_pmo,
            estado_participacion='activo'
        )

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

    #Actualizacion de proyecto. Se verifica que haya al menos un SM y al menos un DV para cerrar el proyecto, de lo contrario error
    def perform_update(self, serializer):
        proyecto_actualizado = serializer.save()

        if proyecto_actualizado.estado_proyecto == "cerrado":
            tiene_scrum_master = Participacion.objects.filter(
                id_proyecto=proyecto_actualizado,
                id_rol__nombre_rol="Scrum Master",
                id_usuario__isnull=False
            ).exists()

            tiene_developer = Participacion.objects.filter(
                id_proyecto=proyecto_actualizado,
                id_rol__nombre_rol="Developer",
                id_usuario__isnull=False
            ).exists()

            if not (tiene_scrum_master and tiene_developer):
                raise serializers.ValidationError(
                    "No puedes cerrar el proyecto sin un Scrum Master y al menos un Developer asignados."
                )

    #Obtener estadisticas de los proyectos asociados al usuario
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        queryset = self.get_queryset()
        ultimo = queryset.last()

        return Response({
            'total_proyectos': queryset.count(),
            'proyectos_activos': queryset.filter(estado_proyecto='activo').count(),
            'proyectos_en_progreso': queryset.filter(estado_proyecto='en_progreso').count(),
            'proyectos_finalizados': queryset.filter(estado_proyecto='finalizado').count(),
            'ultimo_proyecto': {
                'id': ultimo.id_proyecto if ultimo else None,
                'nombre': ultimo.nombre if ultimo else None,
                'estado': ultimo.estado_proyecto if ultimo else None
            }
        })

class InvitarColaboradorView(APIView):
    def post(self, request, *args, **kwargs):
        # 🔐 Autenticación manual desde token
        jwt_authenticator = JWTAuthentication()
        user_auth_tuple = jwt_authenticator.authenticate(request)

        if user_auth_tuple is None:
            return Response({"error": "No autenticado. Token inválido o no proporcionado."}, status=401)

        usuario_jwt, _ = user_auth_tuple
        usuario_que_invita = Usuario.objects.get(id=usuario_jwt.id)

        # ✅ Validar entrada
        serializer = InvitacionColaboradorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        proyecto_id = serializer.validated_data["proyecto_id"]
        rol_id = serializer.validated_data["rol_id"]

        # 🧾 Buscar proyecto
        try:
            proyecto = Proyecto.objects.get(id_proyecto=proyecto_id)
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # 🧑‍💻 Buscar o crear usuario invitado
        usuario, creado = Usuario.objects.get_or_create(email=email)
        if creado:
            usuario.is_active = False
            usuario.set_unusable_password()
            usuario.save()

        # 🔐 Validar rol
        try:
            rol_asignado = Rol.objects.get(id_rol=rol_id)
        except Rol.DoesNotExist:
            return Response({"error": "Rol no válido."}, status=status.HTTP_400_BAD_REQUEST)

        # 🔄 Validación específica para Scrum Master
        if rol_asignado.nombre_rol.lower() == 'scrum_master':
            sm_existente = Participacion.objects.filter(
                id_proyecto=proyecto,
                id_rol=rol_asignado,
                id_usuario__isnull=False
            ).exists()
            if sm_existente:
                return Response({
                    "error": "Ya existe un Scrum Master en este proyecto. Solo puede haber uno."
                }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Validar si el usuario ya participa en el proyecto (con cualquier rol)
        if Participacion.objects.filter(id_usuario=usuario, id_proyecto=proyecto).exists():
            return Response({
                "error": f"El usuario {email} ya está participando en este proyecto como un {rol_asignado}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Buscar si existe un slot libre (sin usuario asignado)
        participacion_existente = Participacion.objects.filter(
            id_usuario=None,
            id_proyecto=proyecto,
            id_rol=rol_asignado
        ).first()

        if participacion_existente:
            # Reutilizar slot
            participacion_existente.id_usuario = usuario
            participacion_existente.invitado_por = usuario_que_invita
            participacion_existente.estado_participacion = "inactivo"
            participacion_existente.save()
            participacion = participacion_existente
        else:
            # Crear nueva participación
            participacion = Participacion.objects.create(
                id_usuario=usuario,
                id_proyecto=proyecto,
                id_rol=rol_asignado,
                estado_participacion="inactivo",
                invitado_por=usuario_que_invita
            )

        # 🔗 Token y URL
        token = default_token_generator.make_token(usuario)
        url = request.build_absolute_uri(
            reverse("completar-registro") + f"?uid={usuario.id}&token={token}"
        )

        # 📬 Enviar correo
        mensaje_email = f"""
🥳 ¡Felicidades!

Has sido invitado a colaborar en el desarrollo del proyecto de software titulado *{proyecto.nombre}*, con el rol de **{rol_asignado.nombre_rol.upper()}**.
Esta invitación ha sido enviada por *{usuario_que_invita}*

🔐 Para completar tu registro y activar tu cuenta, haz clic en el siguiente enlace:

👉 {url}

🧾 Una vez actives tu cuenta podrás acceder a todas las funcionalidades del proyecto.

Si no esperabas esta invitación, puedes ignorar este mensaje.

Saludos,
El equipo de gestión de proyectos de CollabApp 🚀
        """

        send_mail(
            subject="🚀 Invitación a colaborar en un proyecto",
            message=mensaje_email,
            from_email="admin@miapp.com",
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({
        "mensaje": "Participación creada correctamente.",
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
        "id_rol": rol_asignado.id_rol,
        "nombre_rol": rol_asignado.nombre_rol
        },

        "participacion": {
        "estado_participacion": participacion.estado_participacion,
        "rol_id": participacion.id_rol.id_rol
        },

        "invitado_por": {
        "id": usuario_que_invita.id,
        "email": usuario_que_invita.email,
        "nombre_completo": usuario_que_invita.nombre_completo
        },
        "url_registro": url
    }, status=status.HTTP_200_OK)

#Cambiar el rol de un participante en un proyecto
class CambiarRolParticipanteView(APIView):
    def post(self, request):
        serializer = CambiarRolSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        participacion_id = serializer.validated_data["participacion_id"]
        nuevo_rol_id = serializer.validated_data["nuevo_rol_id"]

        try:
            participacion = Participacion.objects.get(id_participacion=participacion_id)
            nuevo_rol = Rol.objects.get(id=nuevo_rol_id)
            proyecto = participacion.id_proyecto
        except (Participacion.DoesNotExist, Rol.DoesNotExist):
            return Response({"error": "Participación o rol no válido."}, status=status.HTTP_400_BAD_REQUEST)
        
        #Validar que el estado de la participación sea 'activo'
        if participacion.estado_participacion != "activo":
            return Response(
                {"error": "Solo se puede cambiar el rol de una participación que se encuentre activa en este proyecto"}
            )

        # Validación: solo un Scrum Master por proyecto
        if nuevo_rol.nombre_rol == 'scrum_master':
            ya_hay_scrum_master = Participacion.objects.filter(
                id_proyecto=proyecto,
                id_rol__nombre_rol='scrum_master'
            ).exclude(id_participacion=participacion_id).exists()

            if ya_hay_scrum_master:
                return Response(
                    {"error": f"Este proyecto '{Proyecto.nombre}'. ya tiene un Scrum Master asignado."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        #Asignar nuevo rol
        participacion.id_rol = nuevo_rol
        participacion.save()

        return Response({"mensaje": "Rol actualizado correctamente."}, status=status.HTTP_200_OK)
    
 
#Prueba formulario básico de registro por invitación con método Post
@csrf_exempt
def completar_registro_view(request):
    uid = request.GET.get("uid")
    token = request.GET.get("token")

    try:
        user = Usuario.objects.get(id=uid)
    except Usuario.DoesNotExist:
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

        # ✅ Activar la participación asociada si estaba en estado "inactivo"
        Participacion.objects.filter(id_usuario=user, estado_participacion="inactivo").update(estado_participacion="activo")

        return HttpResponse("¡Tu cuenta ha sido activada! Ya puedes iniciar sesión.")

    # Si es GET, muestra el formulario
    return HttpResponse(f"""
        <h2>Completar Registro</h2>
        <form method="POST">
            <input type="hidden" name="uid" value="{uid}" />
            <input type="hidden" name="token" value="{token}" />
            <label>Ingresa tu nueva contraseña:</label><br>
            <input type="password" name="password" required/><br><br>
            <button type="submit">Activar cuenta</button>
        </form>
    """)