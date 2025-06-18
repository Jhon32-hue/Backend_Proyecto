"""
Este archivo define señales personalizadas y receptores (`receivers`) asociados al modelo `Historia_usuario`.

Funciones principales:
- Notificar al desarrollador cuando se le asigna una historia de usuario.
- Notificar a los Scrum Masters cuando un desarrollador solicita el cierre de una historia de usuario.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from proyectos.models.hu import Historia_usuario
from usuarios.models.usuario import Usuario

# Señal personalizada para solicitudes de cierre de HU
solicitud_cierre_hu = Signal()

# 📩 Notifica al desarrollador cuando se le asigna una historia de usuario (solo si fue recién creada)
@receiver(post_save, sender=Historia_usuario)
def notificar_asignacion_historia(sender, instance, created, **kwargs):
    """
    Se dispara automáticamente al crear una instancia de Historia_usuario.
    - Envía un correo al usuario asignado (si existe).
    """
    if created and instance.participacion_asignada:
        usuario = instance.participacion_asignada.id_usuario
        send_mail(
            subject="Nueva historia de usuario asignada",
            message=f"Te han asignado la historia: '{instance.titulo}'.",
            from_email="noreply@sistema.com",
            recipient_list=[usuario.email],
            fail_silently=True
        )

# 📩 Notifica a todos los Scrum Masters del proyecto cuando un desarrollador solicita cerrar una HU
@receiver(solicitud_cierre_hu)
def notificar_scrum_master_solicitud_cierre(sender, historia, solicitante, **kwargs):
    """
    Se dispara manualmente desde la vista `SolicitarCierreHUView`.
    - Envía correos individuales a cada Scrum Master asociado al proyecto de la historia.
    - El correo incluye un enlace HTML directo a la historia dentro del proyecto.
    """
    scrum_masters = Usuario.objects.filter(
        participacion__id_proyecto=historia.proyecto,
        participacion__id_rol__nombre_rol="Scrum Master"
    ).distinct()

    for sm in scrum_masters:
        subject = "Solicitud de cierre de historia de usuario"
        from_email = settings.EMAIL_HOST_USER
        to = [sm.email]

        proyecto_url = f"https://collabapp.com/proyectos/{historia.proyecto.id}/hu/{historia.id}"
        text_content = (
            f"{solicitante.nombre} ha solicitado cerrar la historia: '{historia.titulo}'.\n"
            f"Puedes verla en: {proyecto_url}"
        )

        html_content = f"""
        <html>
        <body>
            <p><strong>{solicitante.nombre}</strong> ha solicitado cerrar la historia de usuario:</p>
            <p><strong>{historia.titulo}</strong></p>
            <p>Puedes revisarla en el siguiente enlace:</p>
            <p><a href="{proyecto_url}" style="color:#0057ff;">Ver historia en CollabApp</a></p>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
        except Exception as e:
            print(f"Error al enviar correo a {sm.email}: {e}")
