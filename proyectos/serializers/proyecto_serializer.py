from rest_framework import serializers
from proyectos.models.proyecto import Proyecto

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id_proyecto', 'nombre', 'descripcion', 'estado_proyecto', 'usuario']
        read_only_fields = ['id_proyecto', 'estado_proyecto']
