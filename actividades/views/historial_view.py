from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from actividades.models.historial import Historial_Actividad
from actividades.serializers.historial_serializer import Historial_Actividad_Serializer

class Historial_Actividad_ListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        historial = Historial_Actividad.objects.filter(
            participacion__id_usuario=user
            ).select_related('usuario', 'proyecto', 'tarea', 'participacion')

        # Filtros opcionales que correspondan al proyecto o tarea indicada
        proyecto_id = request.query_params.get('proyecto')
        tarea_id = request.query_params.get('tarea')

        if proyecto_id:
            historial = historial.filter(proyecto_id=proyecto_id)
        if tarea_id:
            historial = historial.filter(tarea_id=tarea_id)

        # Serializador y respuesta
        serializer = Historial_Actividad_Serializer(historial, many=True)
        return Response(serializer.data)
    
    