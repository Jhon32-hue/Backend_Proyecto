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

#Importaciones internas de los módulos
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.rol import Rol
from usuarios.models.usuario import Usuario

from proyectos.serializers.proyecto_serializer import (
    ProyectoSerializer,
    InvitacionColaboradorSerializer,
    CambiarRolSerializer,
    ParticipacionSerializer,
)

#Gestión de operaciones CRUD(create, read, update, delete) Y lógica personalizada de manipulación de proyectos
class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated]

    #Listar proyectos asociados al usuario autenticado
    def get_queryset(self):
        return self.queryset.filter(usuario=self.request.user)

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

#Invitar colaboradores a un proyecto a través de correo
class InvitarColaboradorView(APIView):
    
    #Valida los datos de entrada, los cuales deben incluir correo del colaborador a invitar y el id del proyecto
    def post(self, request, *args, **kwargs):
        serializer = InvitacionColaboradorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        proyecto_id = serializer.validated_data["proyecto_id"]
        rol_id = serializer.validated_data["rol_id"]

        #Se busca el proyecto en la base de datos, si no existe retorna error 404
        try:
            proyecto = Proyecto.objects.get(id_proyecto=proyecto_id) 
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        #Se busca al usuario en la base de datos, si no existe se crea como inactivo (sin contraseña), y se guarda en tabla Usuario
        usuario, creado = Usuario.objects.get_or_create(email=email)

        if creado:
            usuario.is_active = False
            usuario.set_unusable_password()
            usuario.save()

        # 🔐 Validación y asignación del rol
        try:
            rol_asignado = Rol.objects.get(id_rol=serializer.validated_data["rol_id"])
        except Rol.DoesNotExist:
            return Response({"error": "Rol no válido."}, status=status.HTTP_400_BAD_REQUEST)

        # 🧾 Crear la participación con estado "inactivo", y se guarda en el modelo Participación
        participacion, creada = Participacion.objects.get_or_create(
            id_usuario=usuario,
            id_proyecto=proyecto,
            defaults={
            "estado_participacion": "inactivo",
            "id_rol": rol_asignado
            }
        )

        # 🎟️ Generar el token para completar el registro
        token = default_token_generator.make_token(usuario)
        url = request.build_absolute_uri(
            reverse("completar-registro") + f"?uid={usuario.id}&token={token}"
        )           

        # 📬 Enviar el correo de invitación
        send_mail(
            subject="Invitación a colaborar en un proyecto",
            message=f"Has sido invitado a colaborar por tu noviecito. Completa tu registro aquí: {url}",
            from_email="admin@miapp.com",
            recipient_list=[email],
            fail_silently=False,
        )

        # ✅ Respuesta adaptada según si se creó la participación o no
        mensaje = "Participación creada correctamente." if creada else "El usuario ya había sido invitado a este proyecto."
        return Response({
            "mensaje": mensaje,
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
            "estado_participacion": Participacion.estado_participacion,
            "rol_id": Participacion.id_rol
            },
            "participacion_existente": not creada,
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