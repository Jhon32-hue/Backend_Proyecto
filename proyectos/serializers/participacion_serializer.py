from rest_framework import serializers
from proyectos.models.participacion import Participacion
from usuarios.serializers.rol_serializer import Rol_Serializer
from usuarios.serializers.usuario_serializer import Usuario_Serializer  
from proyectos.serializers.proyecto_serializer import ProyectoSerializer 

class ParticipacionProyectoSerializer(serializers.ModelSerializer):
    id_usuario = Usuario_Serializer(read_only=True)
    id_proyecto = ProyectoSerializer(read_only=True)
    id_rol = Rol_Serializer(read_only=True)

    class Meta:
        model = Participacion
        fields = '__all__'
