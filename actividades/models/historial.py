from django.db import models
from proyectos.models.tarea import Tarea
from proyectos.models.participacion import Participacion
from proyectos.models.proyecto import Proyecto
from usuarios.models.usuario import Usuario

class Historial_Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)

    # Relaciones clave
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='actividades_realizadas'
    )

    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name='historial_proyecto',
        null=True, blank=True
    )

    tarea = models.ForeignKey(
        Tarea,
        on_delete=models.CASCADE,
        related_name='historial_actividades',
        null=True, blank=True
    )

    participacion = models.ForeignKey(
        Participacion,
        on_delete=models.CASCADE,
        related_name='actividades',
        null=True, blank=True
    )

    # Detalles de la acción
    accion_realizada = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)

    #Método para mostrar como se ve el objeto cuando se imprime
    def __str__(self):
        rol = self.participacion.rol if self.participacion else "Sin rol"
        proyecto = self.proyecto.nombre if self.proyecto else "Proyecto desconocido"
        return f'{self.usuario} ({rol}) hizo "{self.accion_realizada}" en el proyecto "{proyecto}" el {self.fecha_hora.strftime("%Y-%m-%d %H:%M")}'
