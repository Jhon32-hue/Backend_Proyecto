from rest_framework import serializers
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.usuario import Usuario
from usuarios.models.rol import Rol

# 🔹 Serializer principal para CRUD de proyectos
class ProyectoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proyecto
        fields = ['id_proyecto', 'nombre', 'descripcion', 'estado_proyecto', 'usuario']
        read_only_fields = ['id_proyecto', 'estado_proyecto']

# 🔹 Serializer para invitar colaboradores a un proyecto
class InvitacionColaboradorSerializer(serializers.Serializer):
    email = serializers.EmailField()
    proyecto_id = serializers.IntegerField()
    rol_id = serializers.IntegerField()

    def validate_proyecto_id(self, value):
        if not Proyecto.objects.filter(id_proyecto=value).exists():
            raise serializers.ValidationError("El proyecto especificado no existe.")
        return value

    def validate_rol_id(self, value):
        if not Rol.objects.filter(id_rol=value).exists():
            raise serializers.ValidationError("El rol especificado no existe. Los roles válidos son: 1 (PMO), 2 (Scrum Master), 3 (Developer), 4 (Pendiente)")
        return value
    
# 🔹 Serializer para cambiar el rol de un participante en un proyecto
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

# 🔹 Serializer simplificado de usuario (usado dentro de ParticipacionSerializer)
class UsuarioSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'email']

# 🔹 Serializer simplificado de rol (usado dentro de ParticipacionSerializer)
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = ['id', 'nombre_rol']

# 🔹 Serializer detallado para mostrar participaciones (nested)
class ParticipacionSerializer(serializers.ModelSerializer):
    id_usuario = UsuarioSimpleSerializer()
    id_rol = RolSerializer()
    id_proyecto = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Participacion
        fields = ['id', 'id_usuario', 'id_rol', 'id_proyecto', 'estado_participacion']


# 🔹 Lista proyectos con participaciones anidadas
class ProyectoConParticipacionSerializer(serializers.ModelSerializer):
    participaciones = ParticipacionSerializer(source='participacion_set', many=True)

    class Meta:
        model = Proyecto
        fields = ['id_proyecto', 'nombre', 'descripcion', 'estado_proyecto', 'participaciones']
