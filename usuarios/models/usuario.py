from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

#Configuración para reemplazar username (autentificar ususarios) y modelado de registro de usuarios personalizado

# Manager personalizado
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('El superusuario debe tener is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

# Modelo de usuario personalizado
class Usuario(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    nombre_completo = models.CharField(max_length=255)
    estado_cuenta = models.CharField(max_length=50, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_conexion = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
