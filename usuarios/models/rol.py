from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    ROLES = [
        ('project management', 'Project Management'),
        ('scrum_master', 'Scrum_Master'),
        ('desarrollador', 'Desarrollador'),
    ]
    nombre_rol = models.CharField(max_length=20, choices=ROLES, unique=True)

    def __str__(self):
        return self.get_nombre_rol_display()
