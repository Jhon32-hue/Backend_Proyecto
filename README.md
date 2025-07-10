# 📚 django-rest-agile-projects

API backend desarrollada con Django REST Framework para la gestión de proyectos colaborativos basada en metodologías ágiles. Esta API permite la creación de proyectos, manejo de historias de usuario, asignación de tareas, roles personalizados y sistema de invitaciones, todo esto sumado a la posibilidad de monitorear en tiempo real cada una de las actividades de los colaboradores asignados a los proyectos. Además, esta API cuenta con un sistema de 🔐 Autenticación y Seguridad basado en el el protocolo OAUTH 2.0 y JWT
 monitorear en tiempo real la actividad de cada uno de los colaboradores asignados a los proyectos.

---

## 🧾 Resumen del Proyecto

Este sistema permite a los usuarios:

- 📁 Crear y gestionar proyectos
- 🧩 Administrar historias de usuario (HU) y tareas asociadas
- 👥 Invitar y gestionar colaboradores con distintos roles
- 📜 Visualizar un historial de actividades por proyecto
- 🔐 Autenticación con JWT y flujo de invitaciones con activación
- 🔑 Recuperación de contraseña, login social y verificación por email

---

## 🚀 Tecnologías Utilizadas

- 🐍 Python 3.11+
- 🌐 Django 4.2+
- 🔧 Django REST Framework (DRF)
- 🔐 SimpleJWT para autenticación por tokens
- 📦 dj-rest-auth + allauth (registro/login avanzado)
- 🐘 PostgreSQL como base de datos
- ⚙️ Python-Decouple + Dotenv para configuración por entorno

---

## 🗂️ Modelo Entidad-Relación

> 📌 Diagrama del modelo de base de datos ![image](https://github.com/user-attachments/assets/5b99ea71-c27a-4a03-b4bf-e956072b20bc)

---

## 🧪 Requisitos Previos

Asegúrate de tener instalado en tu sistema:

- Python 3.11+
- PostgreSQL
- Git
- (Opcional) Visual Studio Code

---

## ⚙️ Instalación y Configuración

1. Clona este repositorio: git clone url
2.	Crear entorno virtual: python -m venv venv
2.	Activar entorno: source venv/bin/actívate (Dependiendo del sistema operativo)
3.	Instalar dependencias: pip install -r requirements.txt
4.	Configurar archivo .env
5.	Ejecutar migraciones: python manage.py migrate
6.	Correr servidor: python manage.py runserver



## 🧑‍💻 Autor
Jhoneider Criado
[jhoneideralecxander@gmail.com]

📝 Licencia
Este proyecto está licenciado bajo la MIT License.

⭐ ¿Te fue útil?
¡Dale una estrella al repositorio y compártelo! ⭐

