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
    participacion_asignada = serializers.PrimaryKeyRelatedField(
        queryset=Participacion.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Historia_usuario
        fields = [
            'id',
            'proyecto',
            'participacion_asignada',
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

        if request.method == 'POST':
            proyecto = data.get('proyecto')
            if not proyecto:
                raise serializers.ValidationError("El proyecto es requerido.")

            if not Participacion.objects.filter(
                id_proyecto=proyecto,
                id_usuario=user,
                id_rol__nombre_rol="scrum_master"
            ).exists():
                raise serializers.ValidationError("Solo un Scrum Master puede crear historias de usuario para este proyecto.")

            if Historia_usuario.objects.filter(
                proyecto=proyecto,
                titulo=data.get('titulo'),
                descripcion=data.get('descripcion'),
                participacion_asignada=data.get('participacion_asignada')
            ).exists():
                raise serializers.ValidationError("Ya existe una historia de usuario con el mismo contenido en este proyecto.")

        # No hacer validaciones especiales si es PATCH (update parcial)
        return data
