from django.urls import path
from actividades.views.historial_view import Historial_Actividad_ListView

urlpatterns = [
    path('historial/', Historial_Actividad_ListView.as_view(), name='historial_actividad'),
]
