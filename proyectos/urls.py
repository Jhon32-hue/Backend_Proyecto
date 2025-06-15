from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from proyectos.views.proyecto_view import ProyectoViewSet, InvitarColaboradorView, CambiarRolParticipanteView, completar_registro_view
from proyectos.views.participacion_view import ParticipacionProyectoViewSet

router = DefaultRouter()
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')

# Las acciones personalizadas se accederán mediante:
# /proyectos/{pk}/con-participaciones/
# /proyectos/estadisticas/

urlpatterns = [
    path('', include(router.urls)),
    path('invitar/', InvitarColaboradorView.as_view(), name='invitar-colaborador'),
    path('cambiar-rol/', CambiarRolParticipanteView.as_view(), name='cambiar-rol'),
    path('completar-registro/', completar_registro_view, name='completar-registro'),
    path('participacion/', ParticipacionProyectoViewSet.as_view({'get': 'list'}), name='ver-participacion'),
]