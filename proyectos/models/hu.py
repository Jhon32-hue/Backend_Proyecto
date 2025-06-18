from django.db import models
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion

class Historia_usuario(models.Model):
    ESTADO_POR_HACER = 'por_hacer'
    ESTADO_EN_PROCESO = 'en_proceso'
    ESTADO_CERRADA = 'cerrada'

    ESTADOS = [
        (ESTADO_POR_HACER, 'Por hacer'),
        (ESTADO_EN_PROCESO, 'En proceso'),
        (ESTADO_CERRADA, 'Cerrada'),
    ]

    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name='historias_usuario')
    participacion_asignada = models.ForeignKey(
        Participacion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historias_asignadas',
        help_text='Participación del desarrollador asignado'
    )

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default='por_hacer')
    puntos_historia = models.PositiveIntegerField()
    tiempo_estimado_horas = models.PositiveIntegerField(help_text="Tiempo estimado en horas")

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"[{self.proyecto.nombre}] {self.titulo} - {self.get_estado_display()}"

    class Meta:
        verbose_name = "Historia de Usuario"
        verbose_name_plural = "Historias de Usuario"
