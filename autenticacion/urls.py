from django.urls import path
from autenticacion.views import login_view, google_auth_callback_view


urlpatterns = [
    path('login/', login_view, name='login'),
    path('google/callback/', google_auth_callback_view, name='google_callback'),
]
