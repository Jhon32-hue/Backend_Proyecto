from django.db import models
from django.utils import timezone
from proyectos.models.hu import Historia_usuario
from proyectos.models.participacion import Participacion

class Tarea(models.Model):
    ESTADO_POR_HACER = 'Por hacer'
    ESTADO_EN_PROGRESO = 'En progreso'
    ESTADO_HECHA = 'Hecha'

    OPCIONES_ESTADO = [
        (ESTADO_POR_HACER, 'Por hacer'),
        (ESTADO_EN_PROGRESO, 'En progreso'),
        (ESTADO_HECHA, 'Hecha'),
    ]

    id_tarea = models.AutoField(primary_key=True)
    id_hu = models.ForeignKey(Historia_usuario, on_delete=models.CASCADE, related_name='tareas')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    participacion_asignada = models.ForeignKey(Participacion, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_asignadas')
    estado_tarea = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default=ESTADO_POR_HACER)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Tarea: {self.titulo} ({self.estado_tarea})"