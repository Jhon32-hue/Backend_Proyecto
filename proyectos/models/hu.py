from django.db import models

class Historia_usuario(models.Model):
     ESTADOS = [
        ('Por hacer', 'Por hacer'),
        ('En proceso', 'En proceso'),
        ('Cerrada', 'Cerrada'),
    ]
     
     id_hu = models.AutoField(primary_key=True)
     id_proyecto = models.ForeignKey('Proyecto', on_delete=models.CASCADE, related_name='historias_usuario')
     id_participacion = models.ForeignKey('Participacion', on_delete=models.SET_NULL, null=True, blank=True, related_name='historias_asignadas')
        
     titulo = models.CharField(max_length=255)
     descripcion = models.TextField()
     estado_hu = models.CharField(max_length=20, choices=ESTADOS, default='Por hacer')
     puntos_historia = models.PositiveIntegerField()
     tiempo_estimado = models.PositiveIntegerField(help_text="Tiempo en horas estimadas")

     fecha_creacion = models.DateTimeField(auto_now_add=True)
     fecha_cierre = models.DateTimeField(null=True, blank=True)

     def __str__(self):
            return f"[{self.proyecto.nombre}] {self.titulo} - {self.estado_hu}"

     class Meta:
            verbose_name = "Historia de Usuario"
            verbose_name_plural = "Historias de Usuario"