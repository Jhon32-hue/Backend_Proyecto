from rest_framework import serializers
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.usuario import Usuario
from usuarios.models.rol import Rol


class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id_proyecto', 'nombre', 'descripcion', 'estado_proyecto', 'usuario']
        read_only_fields = ['id_proyecto', 'estado_proyecto']


# Serializer para invitar colaboradores
class InvitacionColaboradorSerializer(serializers.Serializer):
    email = serializers.EmailField()
    proyecto_id = serializers.IntegerField()
    rol_id = serializers.IntegerField()

    def validate_proyecto_id(self, value):
        if not Proyecto.objects.filter(id_proyecto=value).exists():  
            raise serializers.ValidationError("El proyecto especificado no existe.")
        return value



# Serializer para cambiar el rol de un participante
class CambiarRolSerializer(serializers.Serializer):
    participacion_id = serializers.IntegerField()
    nuevo_rol_id = serializers.IntegerField()

    def validate(self, data):
        participacion_id = data.get("participacion_id")
        nuevo_rol_id = data.get("nuevo_rol_id")

        if not Participacion.objects.filter(id=participacion_id).exists():
            raise serializers.ValidationError("La participación no existe.")

        if not Rol.objects.filter(id=nuevo_rol_id).exists():
            raise serializers.ValidationError("El rol especificado no existe.")

        return data


# Serializer simplificado para mostrar datos del usuario (opcional)
class UsuarioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email']


# Serializer para mostrar datos del rol (opcional)
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre_rol']


# Serializer para mostrar datos de la participación (opcional)
class ParticipacionSerializer(serializers.ModelSerializer):
    id_usuario = UsuarioSimpleSerializer()
    id_rol = RolSerializer()
    id_proyecto = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Participacion
        fields = ['id', 'id_usuario', 'id_rol', 'id_proyecto', 'estado_participacion']
