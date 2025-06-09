from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from actividades.models.historial import Historial_Actividad
from actividades.serializers.historial_serializer import Historial_Actividad_Serializer

class Historial_Actividad_ListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(f"[Vista] Usuario: {user} | Autenticado: {user.is_authenticated}")

        # Proyectos en los que participa
        participaciones = user.participacion_set.all()
        proyectos_ids = list(participaciones.values_list('id_proyecto', flat=True))

        # Historial del usuario o proyectos donde participa
        historial = Historial_Actividad.objects.filter(
            Q(proyecto__in=proyectos_ids) | Q(usuario=user)
        ).select_related('usuario', 'proyecto', 'tarea', 'participacion')

        # Filtros opcionales
        proyecto_id = request.query_params.get('proyecto')
        tarea_id = request.query_params.get('tarea')
        hu_id = request.query_params.get('hu')
        participacion_id = request.query_params.get('participacion')

        if proyecto_id:
            try:
                proyecto_id_int = int(proyecto_id)
            except (TypeError, ValueError):
                return Response({'detail': 'ID de proyecto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

            if proyecto_id_int not in proyectos_ids:
                return Response({'detail': 'No tienes permisos para ver este proyecto.'}, status=status.HTTP_403_FORBIDDEN)

            historial = historial.filter(proyecto_id=proyecto_id_int)

        if tarea_id:
            historial = historial.filter(tarea_id=tarea_id)
        if hu_id:
            historial = historial.filter(historia_usuario_id=hu_id)
        if participacion_id:
            historial = historial.filter(participacion_id=participacion_id)

        serializer = Historial_Actividad_Serializer(historial.order_by('-fecha_hora'), many=True)
        return Response(serializer.data)
