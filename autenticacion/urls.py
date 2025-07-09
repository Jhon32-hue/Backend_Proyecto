from django.urls import path
from autenticacion.views import login_view, google_auth_callback_view

urlpatterns = [
    path('google/callback/', google_auth_callback_view, name='google-callback'),
]