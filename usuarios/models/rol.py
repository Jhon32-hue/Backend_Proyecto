from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    ROLES = [
        ('pmo', 'PMO'),
        ('scrum_master', 'Scrum_Master'),
        ('desarrollador', 'Desarrollador'),
    ]

    nombre_rol =models.CharField(max_length=50, unique=True) 
    descripcion =models.TextField(blank=True)

    def __str__(self):
        return f'{self.nombre_rol}'