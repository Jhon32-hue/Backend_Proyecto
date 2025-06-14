from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from proyectos.views.proyecto_view import ProyectoViewSet, InvitarColaboradorView, CambiarRolParticipanteView, completar_registro_view
from proyectos.views.participacion_view import ParticipacionProyectoViewSet

router = DefaultRouter()
router.register(r'proyectos', ProyectoViewSet, basename='proyecto')

urlpatterns = [
    path('proyectos/', include(router.urls)), #Crear proyecto
    path('proyectos/invitar/', InvitarColaboradorView.as_view(), name='invitar-colaborador'), #Invitar colaboradores
    path('proyectos/cambiar-rol/', CambiarRolParticipanteView.as_view(), name='cambiar-rol'), #Cambiar roles
    path("completar-registro/", completar_registro_view, name="completar-registro"),
    path('proyectos/participacion/', ParticipacionProyectoViewSet.as_view({'get': 'list'}), name='ver-participacion'), #Lista proyectos particularmente cada proyecto asociado
]
