from rest_framework import serializers
from usuarios.models.rol import Rol

class Rol_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'