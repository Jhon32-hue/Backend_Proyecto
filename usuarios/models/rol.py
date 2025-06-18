from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    
    ROLES = [
        ('project management', 'Project Management'),
        ('scrum_master', 'Scrum Master'),
        ('developer', 'Developer'),
    ]
    
    nombre_rol = models.CharField(max_length=20, choices=ROLES, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.descripcion and self.nombre_rol != 'Pendiente':
            descripciones = {
                'project management': 'Encargado de la gestión integral del proyecto.',
                'scrum_master': 'Facilitador del equipo Scrum y responsable de remover impedimentos.',
                'developer': 'Responsable de implementar y entregar funcionalidades del producto.',
            }
            self.descripcion = descripciones.get(self.nombre_rol, 'Rol del proyecto')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_nombre_rol_display()
