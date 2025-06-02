from django.db import models

class Tarea(models.Model):
    id_tarea = models.AutoField(primary_key=True)