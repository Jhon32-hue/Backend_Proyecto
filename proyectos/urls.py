from django.urls import path, include
from rest_framework.routers import DefaultRouter
from proyectos.views.proyecto_view import (
    ProyectoViewSet,
    InvitarColaboradorView, 
    GestionInvitacionView,
    CambiarRolParticipanteView,
)
from proyectos.views.hu_view import HistoriaUsuarioViewSet, SolicitarCierreHUView
from proyectos.views.tarea_view import TareaViewSet
from proyectos.views.participacion_view import ParticipacionProyectoViewSet

router = DefaultRouter()
router.register(r'gestion', ProyectoViewSet, basename='proyecto')
router.register(r'historia_usuario', HistoriaUsuarioViewSet, basename='historias')
router.register(r'tareas', TareaViewSet, basename='tareas')

urlpatterns = [
    path('', include(router.urls)),

    # Rutas personalizadas
    path('invitar-colaborador/', InvitarColaboradorView.as_view(), name='invitar-colaborador'),
    path('cambiar-rol/', CambiarRolParticipanteView.as_view(), name='cambiar-rol'),
    path('gestion-invitacion/', GestionInvitacionView.as_view(), name='gestion-invitacion'),
    path('participacion/', ParticipacionProyectoViewSet.as_view({'get': 'list'}), name='ver-participacion'),

    # 🔔 Ruta adicional para solicitar cierre de HU
    path(
        'historia_usuario/<int:pk>/solicitar-cierre/',
        SolicitarCierreHUView.as_view(),
        name='solicitar-cierre-hu'
    ),
]

#25 rutas

'''
✅ 1. RUTAS CRUD GENERADAS POR DefaultRouter
📁 /api/proyectos/gestion/ – Proyectos
Método	Endpoint	Descripción
GET	/api/proyectos/gestion/	Listar proyectos del usuario
POST	/api/proyectos/gestion/	Crear un nuevo proyecto
GET	/api/proyectos/gestion/<id>/	Ver detalles de un proyecto
PUT	/api/proyectos/gestion/<id>/	Actualizar completamente un proyecto
PATCH	/api/proyectos/gestion/<id>/	Actualizar parcialmente un proyecto
DELETE	/api/proyectos/gestion/<id>/	Eliminar un proyecto
GET	/api/proyectos/gestion/<id>/con-participaciones/	Ver proyecto + usuarios asociados (ruta personalizada del ViewSet)

📁 /api/proyectos/historia_usuario/ – Historias de Usuario
Método	Endpoint	Descripción
GET	/api/proyectos/historia_usuario/	Listar historias de usuario del usuario autenticado
POST	/api/proyectos/historia_usuario/	Crear una historia de usuario (solo Scrum Master)
GET	/api/proyectos/historia_usuario/<id>/	Ver detalle de una historia
PUT	/api/proyectos/historia_usuario/<id>/	Actualizar completamente una historia
PATCH	/api/proyectos/historia_usuario/<id>/	Actualizar parcialmente una historia
DELETE	/api/proyectos/historia_usuario/<id>/	Eliminar una historia

📁 /api/proyectos/tareas/ – Tareas
Método	Endpoint	Descripción
GET	/api/proyectos/tareas/	Listar tareas asignadas al usuario
POST	/api/proyectos/tareas/	Crear una nueva tarea (solo si el usuario es asignado a la HU)
GET	/api/proyectos/tareas/<id>/	Ver detalle de una tarea
PUT	/api/proyectos/tareas/<id>/	Actualizar completamente una tarea propia
PATCH	/api/proyectos/tareas/<id>/	Actualizar parcialmente una tarea propia
DELETE	/api/proyectos/tareas/<id>/	Eliminar una tarea (si implementado)

✅ 2. RUTAS PERSONALIZADAS ADICIONALES
📌 Historias
Método	Endpoint	Descripción
POST	/api/proyectos/historia_usuario/<id>/solicitar-cierre/	El desarrollador solicita cierre de HU (si todas las tareas están hechas)

📌 Participación
Método	Endpoint	Descripción
GET	/api/proyectos/participacion/	Listar los proyectos en los que participa el usuario autenticado

📌 Gestión de colaboradores
Método	Endpoint	Descripción
POST	/api/proyectos/invitar-colaborador/	Invitar a un usuario a un proyecto (mediante email)
POST	/api/proyectos/cambiar-rol/	Cambiar el rol de un participante (por un Scrum Master)
POST	/api/proyectos/completar-registro/	Completar el registro de participación de un colaborador invitado

'''