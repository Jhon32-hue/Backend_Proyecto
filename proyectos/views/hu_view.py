"""
Contiene las vistas relacionadas con la gestión de historias de usuario (HU) dentro de un proyecto.
Incluye creación, modificación y solicitud de cierre de HUs.

- `HistoriaUsuarioViewSet`: CRUD de historias de usuario (permite crear, ver, actualizar).
- `SolicitarCierreHUView`: vista específica para que un desarrollador solicite el cierre de una HU.
"""

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.status import HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_200_OK
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from usuarios.models.usuario import Usuario
from proyectos.models.hu import Historia_usuario
from proyectos.models.tarea import Tarea
from proyectos.serializers.hu_serializer import HistoriaUsuarioSerializer
from proyectos.signals import solicitud_cierre_hu


class HistoriaUsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet que gestiona las operaciones CRUD de historias de usuario.
     Reglas clave:
        - Solo muestra historias asociadas al usuario autenticado (por participación).
        - Solo permite cerrar una HU si todas sus tareas están en estado 'Hecha'.
        - Al cerrarse, se registra la fecha de cierre.
    """
    queryset = Historia_usuario.objects.all()
    serializer_class = HistoriaUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Historia_usuario.objects.filter(proyecto__participacion__id_usuario=self.request.user).distinct()

    def perform_update(self, serializer):
        historia = self.get_object()
        nuevo_estado_raw = self.request.data.get('estado', '')
        nuevo_estado = nuevo_estado_raw.lower().strip()  

        if nuevo_estado == Historia_usuario.ESTADO_CERRADA:
            tareas = Tarea.objects.filter(id_hu=historia)
            if not tareas.exists() or tareas.filter(estado_tarea__in=['Por hacer', 'En progreso']).exists():
                raise ValidationError("No se puede cerrar la historia hasta que todas sus tareas estén en estado 'Hecha'.")

            serializer.save(estado=Historia_usuario.ESTADO_CERRADA, fecha_cierre=timezone.now())
        else:
            serializer.save()


class SolicitarCierreHUView(APIView):
    """
    Permite que un desarrollador solicite el cierre de una historia de usuario.
    Condiciones:
        - Solo el desarrollador asignado puede solicitar el cierre.
        - Todas las tareas de la historia deben estar en estado 'Hecha'.
        - Al cumplirse las condiciones, se dispara una señal que notifica a los Scrum Masters del proyecto.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        hu = get_object_or_404(Historia_usuario, pk=pk)

        if not hu.participacion_asignada or hu.participacion_asignada.id_usuario != request.user:
            return Response({"detail": "No tienes permiso para solicitar el cierre de esta HU."}, status=HTTP_403_FORBIDDEN)

        tareas = Tarea.objects.filter(id_hu=hu)
        if not tareas.exists():
            return Response({"detail": "La historia no tiene tareas asociadas."}, status=HTTP_400_BAD_REQUEST)

        tareas_pendientes = tareas.exclude(estado_tarea__iexact='hecha')
        if tareas_pendientes.exists():
            return Response({
                "detail": "No puedes solicitar el cierre hasta que todas las tareas estén en 'Hecha'.",
                "tareas_pendientes": list(tareas_pendientes.values('id_tarea', 'titulo', 'estado_tarea'))
            }, status=HTTP_400_BAD_REQUEST)

        # 🔔 Disparar la señal
        solicitud_cierre_hu.send(sender=self.__class__, historia=hu, solicitante=request.user)

        return Response({"detail": "Solicitud de cierre enviada al Scrum Master."}, status=HTTP_200_OK)
