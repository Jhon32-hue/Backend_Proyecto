"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),

    # Rutas por aplicacion
    path('api/proyectos/', include('proyectos.urls')), #/{id}/ (Se puede actualizar, detallar o eliminar proyecto), /estadisticas/, /invitar/, /cambiar-rol/

    path('api/usuarios/', include('usuarios.urls')),  #/token/, /registro/, /perfil/, /listar/, /actualizar/, /eliminar/, /roles/, /recuperar-contraseña/, /confirmar-contraseña/
    path('api/historial/', include('actividades.urls')),
    path ('api/', include('proyectos.urls')),

    #Rutas para inicio y registro de sesión OAuth2
    path('auth/', include('dj_rest_auth.urls')),  # Habilita login con contraseña
    path('auth/registration/', include('dj_rest_auth.registration.urls')),  # Registra a los usuarios que inician sesión con OAuth
    path('auth/social/', include('allauth.socialaccount.urls')),  # Selecciona el proveedor  Google, etc)
    path('auth/accounts/', include('allauth.urls')), #Callback desde el proveedor. Completa la url anterior


]
