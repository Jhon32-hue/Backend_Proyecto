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
        read_only_fields = ['id_proyecto', 'usuario']

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

#Cambiar rol de un participante    
class CambiarRolSerializer(serializers.Serializer):
    id_usuario = serializers.IntegerField()
    id_proyecto = serializers.IntegerField()
    nuevo_rol = serializers.CharField()
    rol_anterior = serializers.CharField(read_only=True)  # Opcional, si lo quieres incluir

    def validate(self, data):
        id_usuario = data.get("id_usuario")
        id_proyecto = data.get("id_proyecto")
        nuevo_rol = data.get("nuevo_rol")

        # Validar existencia de usuario y proyecto
        if not Usuario.objects.filter(id=id_usuario).exists():
            raise serializers.ValidationError({"id_usuario": "El usuario no existe."})

        if not Proyecto.objects.filter(id_proyecto=id_proyecto).exists():
            raise serializers.ValidationError({"id_proyecto": "El proyecto no existe."})

        # Validar participación activa
        try:
            participacion = Participacion.objects.get(
                id_usuario=id_usuario,
                id_proyecto=id_proyecto,
                estado_participacion="activo"
            )
        except Participacion.DoesNotExist:
            raise serializers.ValidationError("El usuario no participa activamente en este proyecto.")

        # Validar rol válido
        nombres_validos = Rol.objects.values_list('nombre_rol', flat=True)
        if nuevo_rol not in nombres_validos:
            raise serializers.ValidationError({
                "nuevo_rol": f"Rol no válido. Debe ser uno de: {list(nombres_validos)}"
            })

        # Validar que el nuevo rol no sea igual al actual
        if participacion.id_rol.nombre_rol == nuevo_rol:
            raise serializers.ValidationError({
                "nuevo_rol": "El nuevo rol no puede ser igual al rol actual."
            })

        # Agregar el rol anterior como un valor validado (lo puedes usar en la vista)
        data["rol_anterior"] = participacion.id_rol.nombre_rol

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
        fields = ['id_rol', 'nombre_rol']

# 🔹 Serializer detallado para mostrar participaciones (nested)
class ParticipacionSerializer(serializers.ModelSerializer):
    id_usuario = UsuarioSimpleSerializer()
    id_rol = RolSerializer()
    id_proyecto = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Participacion
        fields = ['id_participacion', 'id_usuario', 'id_rol', 'id_proyecto', 'estado_participacion']


# 🔹 Lista proyectos con participaciones anidadas
class ProyectoConParticipacionSerializer(serializers.ModelSerializer):
    participaciones = ParticipacionSerializer(source='participacion_set', many=True)

    class Meta:
        model = Proyecto
        fields = '__all__'
