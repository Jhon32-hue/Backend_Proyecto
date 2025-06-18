from rest_framework import serializers
from proyectos.models.participacion import Participacion
from usuarios.models.rol import Rol
from usuarios.models.usuario import Usuario
from proyectos.models.proyecto import Proyecto
from usuarios.serializers.rol_serializer import Rol_Serializer
from usuarios.serializers.usuario_serializer import Usuario_Serializer  
from proyectos.serializers.proyecto_serializer import ProyectoSerializer 

class Rol_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id_rol', 'nombre_rol', 'descripcion']

class Usuario_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email', 'nombre_completo']

class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id_proyecto', 'nombre']  

class ParticipacionDetalleSerializer(serializers.ModelSerializer):
    id_usuario = Usuario_Serializer(read_only=True)
    id_proyecto = ProyectoSerializer(read_only=True)
    id_rol = Rol_Serializer(read_only=True)

    class Meta:
        model = Participacion
        fields = [
            'id_participacion',
            'id_usuario',
            'id_proyecto',
            'id_rol',
            'estado_participacion',
            'fecha_incorporacion'
        ]

