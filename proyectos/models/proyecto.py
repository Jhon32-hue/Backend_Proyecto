from django.db import models
from usuarios.models.usuario import Usuario

#Por ahora esto solo me permite crear proyectos
class Proyecto(models.Model):
    id_proyecto = models.AutoField(primary_key=True)
    ESTADOS = [
        ('activo', 'Activo'),
        ('en_progreso', 'En progreso'),
        ('finalizado', 'Finalizado'),
    ]

    #Relaciones clave
    nombre = models.CharField(max_length=255)
    descripcion =models.TextField()
    fecha_creacion =models.DateField(auto_now_add = True)
    estado_proyecto = models.CharField(max_length=50, choices=ESTADOS, default='activo')

 # Relación con el usuario creador
    usuario = models.ForeignKey(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='proyectos_creados'
    )

    def __str__(self):
        return f'El proyecto: {self.nombre} se encuentra en estado ({self.estado_proyecto})'