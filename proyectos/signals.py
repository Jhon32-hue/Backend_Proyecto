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
from proyectos.models.tarea import Tarea


# Señal personalizada para solicitudes de cierre de HU
solicitud_cierre_hu = Signal()

#Asignación automática de estado al crear una HU
@receiver(post_save, sender=Historia_usuario)
def asignar_estado_en_proceso_si_asignada(sender, instance, created, **kwargs):
    """
    Cambia automáticamente el estado a 'en_proceso' si la historia fue creada con una participación asignada.
    Esto evita tener que establecerlo manualmente desde el serializador.
    """
    if created and instance.participacion_asignada and instance.estado != 'en_proceso':
        instance.estado = 'en_proceso'
        instance.save()


# 📩 Notifica a todos los Scrum Masters del proyecto cuando un desarrollador solicita cerrar una HU
@receiver(solicitud_cierre_hu)
def notificar_scrum_master_solicitud_cierre(sender, historia, solicitante, **kwargs):
    print("🔔 Señal recibida para solicitud de cierre")
    
    """
            Se dispara desde la vista `SolicitarCierreHUView`.
    """
    scrum_masters = Usuario.objects.filter(
        participacion__id_proyecto=historia.proyecto,
        participacion__id_rol__nombre_rol="scrum_master"
    ).distinct()

    for sm in scrum_masters:
        subject = "Solicitud de cierre de historia de usuario"
        from_email = settings.EMAIL_HOST_USER
        to = [sm.email]

        proyecto_url = f"https://collabapp.com/proyectos/{historia.proyecto_id}/hu/{historia.id}"
        text_content = f"{solicitante.nombre_completo} ha solicitado cerrar la historia: '{historia.titulo}'.\nPuedes verla en: {proyecto_url}"

        html_content = f"""
        <html>
        <body>
            <p><strong>{solicitante.nombre_completo}</strong> ha solicitado cerrar la historia de usuario:</p>
            <p><strong>{historia.titulo}</strong></p>
            <p>Puedes revisarla en el siguiente enlace:</p>
            <a href="{proyecto_url}">Ver historia</a>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        try:
            msg.send()
        except Exception as e:
            print(f"Error al enviar email: {e}")


#Notifica al desarrollador cuando se le asigna una historia de usuario al momento de crearla.
@receiver(post_save, sender=Historia_usuario)
def notificar_asignacion_historia_usuario(sender, instance, created, **kwargs):
    
    if created and instance.participacion_asignada:
        print(f"✅ Señal ejecutada para historia: {instance.titulo}")

        usuario = instance.participacion_asignada.id_usuario
        email = usuario.email

        subject = "Nueva historia de usuario asignada"
        from_email = settings.EMAIL_HOST_USER
        to = [email]

        historia_url = f"https://collabapp.com/proyectos/{instance.proyecto_id}/hu/{instance.id}"
        text_content = (
            f"Se te ha asignado una nueva historia de usuario:\n"
            f"'{instance.titulo}'\n\n"
            f"Descripción: {instance.descripcion}\n"
            f"Puedes revisarla aquí: {historia_url}"
        )

        html_content = f"""
        <html>
        <body>
            <p>Se te ha asignado una nueva historia de usuario:</p>
            <p><strong>{instance.titulo}</strong></p>
            <p>{instance.descripcion}</p>
            <p>Puedes verla en el siguiente enlace:</p>
            <a href="{historia_url}">Ver historia</a>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")

        try:
            msg.send()
        except Exception as e:
            print(f"❌ Error al enviar email al desarrollador asignado a HU: {e}")