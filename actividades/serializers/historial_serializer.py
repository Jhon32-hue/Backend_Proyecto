from rest_framework import serializers
from actividades.models.historial import Historial_Actividad

class Historial_Actividad_Serializer(serializers.ModelSerializer):
    nombre_usuario = serializers.StringRelatedField(source='usuario', read_only=True)
    nombre_proyecto = serializers.StringRelatedField(source='proyecto', read_only=True)
    nombre_tarea = serializers.StringRelatedField(source='tarea', read_only=True)
    rol_participacion = serializers.StringRelatedField(source='participacion', read_only=True)

    class Meta:
        model = Historial_Actividad
        fields = [
            'id_actividad',
            'usuario',
            'nombre_usuario',
            'proyecto',
            'nombre_proyecto',
            'tarea',
            'nombre_tarea',
            'participacion',
            'rol_participacion',
            'accion_realizada',
            'fecha_hora',
        ]

#Método para asegurar que toda actividad esté asociada al menos a un proyecto o a una tarea.
    def validate(self, data):
    # Toda actividad debe tener al menos un proyecto asociado
        if not data.get('proyecto'):
            raise serializers.ValidationError(
            "Toda actividad debe estar asociada a un proyecto."
        )
        return data

 
 