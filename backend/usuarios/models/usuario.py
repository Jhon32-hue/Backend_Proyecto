from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


#Configuración para reemplazar username por email como dato para autentificar ususarios
class UserManager(BaseUserManager):
    def create_user(self, email, password= None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        user = self.model(email = email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password= None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El super usuario debe ser un staff')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El super usuario debe tener en verdadero el campo is_superusuario')
        
        return self.create_user(email, password, **extra_fields)


#Importante que herede de AbstracUser que es la configuracion por defecto
class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Dirección de correo electrónico')
    username = None #Elimino el campo username que trae por defecto Django para pedir el email
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    