from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from usuarios.models.usuario import Usuario
from usuarios.serializers.usuario_serializer import Usuario_Serializer
from django.utils import timezone
from rest_framework.permissions import AllowAny



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = Usuario.USERNAME_FIELD
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['nombre_completo'] = user.nombre_completo
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        #Actualización de la última conexión
        self.user.ultima_conexion = timezone.now()
        self.user.save(update_fields=['ultima_conexion'])


        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['nombre_completo'] = self.user.nombre_completo
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioRegistroView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = Usuario_Serializer
    permission_classes = [AllowAny] 