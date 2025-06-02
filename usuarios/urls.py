from django.urls import path
from usuarios.views.usuario_view import CustomTokenObtainPairView, UsuarioRegistroView

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('registro/', UsuarioRegistroView.as_view(), name='registro_usuario'),
]
