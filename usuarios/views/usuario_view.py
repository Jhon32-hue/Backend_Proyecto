from rest_framework import generics, status
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from usuarios.models.usuario import Usuario
from usuarios.serializers.usuario_serializer import Usuario_Serializer, CustomTokenObtainPairSerializer, UsuarioUpdateSerializer
from usuarios.serializers.usuario_serializer import (
    EnviarCodigoRecuperacionSerializer,
    ConfirmarCodigoRecuperacionSerializer,
    Usuario_Serializer
)

#Obtiene el serialziador para generar un token personalizado JWT
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Clases para USUARIO: REGISTRO Y GESTIÓN
class UsuarioRegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = Usuario_Serializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Crear el usuario
        user = serializer.save()

        # Generar el token JWT
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Asegúrate de que el token se genera correctamente
        print(f"Token generado: {access_token}")

        # Devolver la respuesta con el token y los datos del usuario
        return Response({
            "accessToken": access_token,  # Incluye el token aquí
            "user": {
                "id": user.id,
                "email": user.email,
                "nombre_completo": user.nombre_completo,
                "estado_cuenta": user.estado_cuenta,
                "fecha_registro": user.fecha_registro,
                "ultima_conexion": user.ultima_conexion,
                "is_active": user.is_active
            }
        }, status=status.HTTP_201_CREATED)
    
 #Devuelve los datos del usuario
class UsuarioPerfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = Usuario_Serializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = Usuario_Serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

            if not user.codigo_esta_vigente():
                return Response({"detail": "Código expirado."}, status=400)

            user.set_password(nueva_password)
            user.codigo_recuperacion = None
            user.codigo_generado_en = None
            user.save()

            return Response({"detail": "Contraseña actualizada con éxito."})
        
        return Response(serializer.errors, status=400)
