from django.urls import path
from usuarios.views.usuario_view import CustomTokenObtainPairView, UsuarioRegistroView
from usuarios.views.rol_view import RolViewSet


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('registro/', UsuarioRegistroView.as_view(), name='registro_usuario'),
    path('roles/', RolViewSet.as_view({'get': 'list'}), name='ver-roles'),
]
