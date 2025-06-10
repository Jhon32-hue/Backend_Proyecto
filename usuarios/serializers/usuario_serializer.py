from rest_framework import serializers
from usuarios.models.usuario import Usuario
from dj_rest_auth.registration.serializers import RegisterSerializer


class Usuario_Serializer (serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre_completo', 'estado_cuenta',
            'fecha_registro', 'ultima_conexion', 'is_active', 'password'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_conexion', 'is_active']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class CustomRegisterSerializer(RegisterSerializer):
    username = None  # <- Desactiva por completo el campo username
    email = serializers.EmailField(required=True)
    nombre_completo = serializers.CharField(required=True)

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'nombre_completo': self.validated_data.get('nombre_completo', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
        }