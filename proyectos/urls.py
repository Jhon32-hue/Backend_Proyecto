from django.urls import path, include
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from proyectos.views.proyecto_view import ProyectoViewSet
from proyectos.views.participacion_view import ParticipacionProyectoViewSet

router = DefaultRouter()
router.register(r'', ProyectoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('participacion/', ParticipacionProyectoViewSet.as_view({'get': 'list'}), name='ver-participacion'),
]
