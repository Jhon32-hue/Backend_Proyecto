from rest_framework import serializers
from django.utils import timezone
from usuarios.models.usuario import Usuario
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

#Registro_Usuario
class Usuario_Serializer (serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'nombre_completo', 'estado_cuenta',
            'fecha_registro', 'ultima_conexion', 'is_active', 'password'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_conexion', 'is_active', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

# AUTH: TOKEN JWT PERSONALIZADO
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

        # Actualizar última conexión
        self.user.ultima_conexion = timezone.now()
        self.user.save(update_fields=['ultima_conexion'])

        # Agregar info adicional al token
        data['user_id'] = self.user.id
        data['email'] = self.user.email
        data['nombre_completo'] = self.user.nombre_completo
        return data

#Actualizacion de datos
class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['email', 'nombre_completo']
        extra_kwargs = {
            'email': {'required': False},
            'nombre_completo': {'required': False},
        }

    def validate_email(self, value):
        user = self.context['request'].user
        if Usuario.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está en uso por otro usuario.")
        return value

#Sobreescribir Username por email
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

#Cambiar contraseña
class EnviarCodigoRecuperacionSerializer(serializers.Serializer):
    email = serializers.EmailField()

#Validación de cambio de contraseña
class ConfirmarCodigoRecuperacionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    codigo = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_password(self, value):
        validate_password(value)  # Esto usa validadores de Django como mínimo 8, no común, etc.
        return value