from django.db import models
from django.utils import timezone
from usuarios.models.usuario import Usuario
from proyectos.models.proyecto import Proyecto
from usuarios.models.rol import Rol

class Participacion(models.Model):
    id_participacion = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.SET_NULL, null=True, blank=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    estado_participacion = models.CharField(max_length=20, choices=[
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo')
    ])
    fecha_incorporacion = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.id_usuario} está participando como {self.id_rol} en {self.id_proyecto}"
