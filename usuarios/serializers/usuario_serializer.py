from rest_framework import serializers
from usuarios.models.usuario import Usuario

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