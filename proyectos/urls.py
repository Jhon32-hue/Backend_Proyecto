from django.urls import path
from proyectos.views.proyecto_view import CrearProyectoView

urlpatterns = [
    path('create/', CrearProyectoView.as_view(), name='crear-proyecto'),
]
