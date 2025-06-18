from django.urls import path, include
from rest_framework.routers import DefaultRouter
from proyectos.views.proyecto_view import (
    ProyectoViewSet,
    InvitarColaboradorView,
    CambiarRolParticipanteView,
    completar_registro_view
)
from proyectos.views.participacion_view import ParticipacionProyectoViewSet

# ✅ Prefijo 'gestion' evita que las rutas se pisen con las personalizadas
router = DefaultRouter()
router.register(r'gestion', ProyectoViewSet, basename='proyecto')

urlpatterns = [
    # ✅ CRUD de proyectos + acciones personalizadas como /con-participaciones/
    path('', include(router.urls)),

    # ✅ Rutas personalizadas separadas
    path('invitar-colaborador/', InvitarColaboradorView.as_view(), name='invitar-colaborador'),
    path('cambiar-rol/', CambiarRolParticipanteView.as_view(), name='cambiar-rol'),
    path('completar-registro/', completar_registro_view, name='completar-registro'),

    # ✅ Vista personalizada para listar participaciones de usuario
    path('participacion/', ParticipacionProyectoViewSet.as_view({'get': 'list'}), name='ver-participacion'),
]

'''Rutas generadas automáticamente por DefaultRouter

GET /api/proyectos/gestion/ — listar proyectos

POST /api/proyectos/gestion/ — crear proyecto

GET /api/proyectos/gestion/<pk>/ — ver detalle

PUT /api/proyectos/gestion/<pk>/ — actualizar completo

PATCH /api/proyectos/gestion/<pk>/ — actualizar parcial

DELETE /api/proyectos/gestion/<pk>/ — eliminar

GET /api/proyectos/gestion/<pk>/con-participaciones/

'''