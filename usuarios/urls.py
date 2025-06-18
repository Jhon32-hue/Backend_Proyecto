from django.urls import path
from usuarios.views.rol_view import RolListarView
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

urlpatterns = [
    # Autenticación (login)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),#✅ (post)

    # Registro
    path('registro/', UsuarioRegistroView.as_view(), name='registro_usuario'),#✅ (post)

    # Perfil del usuario autenticado
    path('perfil/', UsuarioPerfilView.as_view(), name='ver_perfil_usuario'),#✅(get)

    # Listado de usuarios (visible solo para superusuarios/staff)
    path('listar/',UsuarioListView.as_view(), name='listar_usuarios'),#✅(get, solo superUser)

    # Actualizar perfil del usuario autenticado
    path('actualizar/', UsuarioUpdateView.as_view(), name='actualizar_usuario'),#✅ (put, solo nombre o email)

    # Eliminar cuenta del usuario autenticado
    path('eliminar/', UsuarioDeleteView.as_view(), name='eliminar_usuario'), #✅ (delete, solo nombre o email)

    # Roles
    path('roles/', RolListarView.as_view(), name='ver_roles'), #✅ (Solo el super User puede ver los roles disponibles)

    #Recuperar contraseña
    path('recuperar-contraseña/', EnviarCodigoRecuperacionView.as_view(), name='password_reset'),#✅ (post)

    #Confirmar código_recuperación
    path('confirmar-codigo/', ConfirmarCodigoRecuperacionView.as_view(), name='confirmar_codigo'), #✅ (post)
]
