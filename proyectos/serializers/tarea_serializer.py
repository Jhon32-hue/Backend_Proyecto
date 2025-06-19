from rest_framework import serializers
from proyectos.models.tarea import Tarea

class TareaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tarea
        fields = '__all__'
        read_only_fields = ['id_tarea', 'fecha_creacion', 'fecha_actualizacion']

    def validate(self, data):
        user = self.context['request'].user
        hu = data.get('id_hu')
        participacion = data.get('participacion_asignada')

        # Validación para creación
        if self.instance is None:
            if not hu or not hu.participacion_asignada:
                raise serializers.ValidationError("La historia no tiene un desarrollador asignado.")

            if hu.participacion_asignada.id_usuario != user:
                raise serializers.ValidationError("Solo el desarrollador asignado puede crear tareas para esta HU.")

            if participacion and participacion.id_usuario != user:
                raise serializers.ValidationError("No puedes asignar esta tarea a otro usuario.")
            
            # ⚠️ Validar que no exista ya una historia igual
            if Tarea.objects.filter(
                titulo=data['titulo'],
                descripcion=data['descripcion'],
                participacion_asignada=data.get('participacion_asignada')
            ).exists():
                raise serializers.ValidationError("Ya existe una tarea creada con el mismo contenido en esta Historia de Usuario.")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
