from django.urls import path
from usuarios.views.usuario_view import (
    CustomTokenObtainPairView,
    UsuarioRegistroView,
    UsuarioPerfilView,
    UsuarioListView,
    UsuarioUpdateView,
    UsuarioDeleteView,
    EnviarCodigoRecuperacionView,
    ConfirmarCodigoRecuperacionView,
)
from usuarios.views.rol_view import RolViewSet
from proyectos.views.proyecto_view import (),

urlpatterns = [
    # Autenticación (login)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Registro
    path('registro/', UsuarioRegistroView.as_view(), name='registro_usuario'),

    # Perfil del usuario autenticado
    path('perfil/', UsuarioPerfilView.as_view(), name='ver_perfil_usuario'),

    # Listado de usuarios (visible solo para superusuarios/staff)
    path('listar/',UsuarioListView.as_view(), name='listar_usuarios'),

    # Actualizar perfil del usuario autenticado
    path('actualizar/', UsuarioUpdateView.as_view(), name='actualizar_usuario'),

    # Eliminar cuenta del usuario autenticado
    path('eliminar/', UsuarioDeleteView.as_view(), name='eliminar_usuario'),

    # Roles
    path('roles/', RolViewSet.as_view({'get': 'list'}), name='ver_roles'),

    #Recuperar contraseña
    path('recuperar-contraseña', EnviarCodigoRecuperacionView.as_view(), name='password_reset'),

    #Confirmar código_recuperación
    path('confirmar-contraseña/', ConfirmarCodigoRecuperacionView.as_view(), name='confirmar_codigo'),
]
