from rest_framework import viewsets
from proyectos.models.participacion import Participacion
from proyectos.serializers.participacion_serializer import ParticipacionProyectoSerializer
from rest_framework.permissions import IsAuthenticated

class ParticipacionProyectoViewSet(viewsets.ModelViewSet):
    queryset = Participacion.objects.all()
    serializer_class = ParticipacionProyectoSerializer
    permission_classes = [IsAuthenticated]
