from django.urls import path
from actividades.views.historial_view import Historial_Actividad_ListView

urlpatterns = [
    path('', Historial_Actividad_ListView.as_view(), name='historial_actividad'), #Lista acciones realizadas (save o delete) en Proyectos, Tareas o Historia_Usuario
]
