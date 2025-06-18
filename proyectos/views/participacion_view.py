from rest_framework import viewsets
from proyectos.models.participacion import Participacion
from proyectos.serializers.participacion_serializer import ParticipacionDetalleSerializer
from rest_framework.permissions import IsAuthenticated

class ParticipacionProyectoViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipacionDetalleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Participacion.objects.all()
        return Participacion.objects.filter(id_usuario=user)
