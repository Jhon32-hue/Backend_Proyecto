"""
Serializador para el modelo Historia_usuario.
Se encarga de la validación de datos y creación de historias de usuario.
    Lógica adicional:
    - Verifica que el usuario autenticado tenga el rol de Scrum Master para poder crear historias.
"""

from rest_framework import serializers
from proyectos.models.hu import Historia_usuario
from proyectos.models.participacion import Participacion

class HistoriaUsuarioSerializer(serializers.ModelSerializer):
    id_participacion = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = Historia_usuario
        fields = [
            'id',
            'proyecto',
            'id_participacion',
            'titulo',
            'descripcion',
            'estado',
            'puntos_historia',
            'tiempo_estimado_horas',
            'fecha_cierre'
        ]
        read_only_fields = ['id', 'estado', 'fecha_cierre']

    def validate(self, data):
        """
        Valida que el usuario actual sea Scrum Master del proyecto especificado.
        Esta restricción aplica solo durante la creación de una historia.
        """
        request = self.context['request']
        user = request.user
        proyecto = data['proyecto']

        if not Participacion.objects.filter(
            id_proyecto=proyecto,
            id_usuario=user,
            id_rol__nombre_rol="Scrum Master"
        ).exists():
            raise serializers.ValidationError("Solo un Scrum Master puede crear historias de usuario para este proyecto.")

        return data

    def create(self, validated_data):
        id_participacion = validated_data.pop('id_participacion', None)
        historia = Historia_usuario.objects.create(**validated_data)

        if id_participacion:
            try:
                participacion = Participacion.objects.get(id=id_participacion)
                historia.participacion_asignada = participacion
                historia.save()
            except Participacion.DoesNotExist:
                raise serializers.ValidationError("La participación asignada no existe.")

        return historia