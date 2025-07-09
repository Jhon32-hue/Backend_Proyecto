📚 Documentación Técnica API - Backend Django REST Framework

1. 🧾 Resumen del Proyecto
Este backend implementa un sistema de gestión de proyectos basado en metodologías ágiles, permitiendo a los usuarios:
●	Crear y gestionar proyectos
●	Administrar historias de usuario (HU) y tareas
●	Invitar y gestionar colaboradores con diferentes roles
●	Visualizar un historial de actividades
El sistema también permite autenticación por JWT, recuperación de contraseña y administración de roles de usuario.

3.Tecnologías Utilizadas
●	Python 3.11+
●	Django 4.2+
●	Django REST Framework (DRF)
●	SimpleJWT para autenticación con tokens
●	dj-rest-auth + allauth para login y registro
●	PostgreSQL como base de datos principal
●	dotenv + decouple para variables de entorno

4. Modelo de Entidad-Relación BD
5. ![image](https://github.com/user-attachments/assets/5b99ea71-c27a-4a03-b4bf-e956072b20bc)


# Como ejecutar el proyecto

## Requerimientos

- Python
- Postgresql
- Visual Studio Code

## Clonar repositorio

 5.⚙️ Instalación y Configuración
1.	Crear entorno virtual: python -m venv venv
2.	Activar entorno: source venv/bin/actívate (Dependiendo del sistema operativo)
3.	Instalar dependencias: pip install -r requirements.txt
4.	Configurar archivo .env
5.	Ejecutar migraciones: python manage.py migrate
6.	Correr servidor: python manage.py runserver

##Continua localmente
