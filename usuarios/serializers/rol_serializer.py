from rest_framework import serializers
from usuarios.models.rol import Rol


class Rol_Serializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='id_rol')

    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre_rol', 'descripcion']
