from rest_framework import viewsets, status, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from proyectos.models.tarea import Tarea
from proyectos.models.hu import Historia_usuario
from proyectos.serializers.tarea_serializer import TareaSerializer

class TareaViewSet(viewsets.ModelViewSet):
    """
    CRUD de tareas.
    Reglas:
    - Solo desarrolladores asignados pueden crear tareas para su HU.
    - Solo pueden actualizar tareas que les han sido asignadas.
    - Solo pueden cambiar el estado de sus tareas.
    """
    queryset = Tarea.objects.all()
    serializer_class = TareaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Tarea.objects.filter(participacion_asignada__id_usuario=user)

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        tarea = self.get_object()
        user = self.request.user
        if tarea.participacion_asignada and tarea.participacion_asignada.id_usuario != user:
            raise serializers.ValidationError("No puedes modificar tareas que no te pertenecen.")
        serializer.save()
