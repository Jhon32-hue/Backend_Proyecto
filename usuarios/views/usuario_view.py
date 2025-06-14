from rest_framework import generics, status
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from usuarios.models.usuario import Usuario
from usuarios.serializers.usuario_serializer import Usuario_Serializer, CustomTokenObtainPairSerializer, UsuarioUpdateSerializer
from usuarios.serializers.usuario_serializer import (
    EnviarCodigoRecuperacionSerializer,
    ConfirmarCodigoRecuperacionSerializer,
)

#Obtiene el serialziador para generar un token personalizado JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Clases para USUARIO: REGISTRO Y GESTIÓN
class UsuarioRegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = Usuario_Serializer
    permission_classes = [AllowAny]
    
 #Devuelve los datos del usuario
class UsuarioPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = Usuario_Serializer(request.user)
        return Response(serializer.data)

 #Lista todos los usuarios si el solicitante es superuser o staff. Si no, devuelve solo su propio perfil.
class UsuarioListView(generics.ListAPIView):
    serializer_class = Usuario_Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Usuario.objects.all()
        return Usuario.objects.filter(id=user.id)

#Actualización de datos
class UsuarioUpdateView(generics.UpdateAPIView):    
    serializer_class = UsuarioUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):    # Permitir actualizaciones parciales (solo campos enviados)
        return self.partial_update(request, *args, **kwargs)
    
 #Permite al usuario eliminar su cuenta.
class UsuarioDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
      

# RECUPERAR CONTRASEÑA
class EnviarCodigoRecuperacionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EnviarCodigoRecuperacionSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return Response({"detail": "Usuario no encontrado."}, status=404)

            user.generar_codigo_recuperacion()
            send_mail(
                "Código de recuperación",
                f"Hola {user.nombre_completo}, tu código es: {user.codigo_recuperacion}",
                "no-reply@tusitio.com",
                [user.email],
            )
            return Response({"detail": "Código enviado al correo."})
        return Response(serializer.errors, status=400)

#Validación del código de recuperación
class ConfirmarCodigoRecuperacionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmarCodigoRecuperacionSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            codigo = serializer.validated_data["codigo"]
            nueva_password = serializer.validated_data["password"]

            try:
                user = Usuario.objects.get(email=email)
            except Usuario.DoesNotExist:
                return Response({"detail": "Usuario no encontrado."}, status=404)

            if user.codigo_recuperacion != codigo:
                return Response({"detail": "Código incorrecto."}, status=400)

            if user.codigo_expira < timezone.now():
                return Response({"detail": "Código expirado."}, status=400)

            user.set_password(nueva_password)
            user.codigo_recuperacion = None
            user.codigo_expira = None
            user.save()

            return Response({"detail": "Contraseña actualizada con éxito."})
        return Response(serializer.errors, status=400)
