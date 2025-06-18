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
    """
    Notifica a todos los Scrum Masters del proyecto cuando un desarrollador solicita cerrar una HU.
    Se dispara desde la vista `SolicitarCierreHUView`.
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
        text_content = f"{solicitante.nombre} ha solicitado cerrar la historia: '{historia.titulo}'.\nPuedes verla en: {proyecto_url}"

        html_content = f"""
        <html>
        <body>
            <p><strong>{solicitante.nombre}</strong> ha solicitado cerrar la historia de usuario:</p>
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


# 📩 Notifica al desarrollador cuando se le asigna una historia de usuario (solo si fue recién creada)
@receiver(post_save, sender=Tarea)
def notificar_asignacion_o_reasignacion_tarea(sender, instance, created, **kwargs):
    """
    Notifica al desarrollador cuando:
    - Se crea una nueva tarea con participación asignada.
    - Se actualiza una tarea y cambia la participación asignada.
    """
    if not instance.participacion_asignada:
        return  # No hay nadie asignado, no se notifica

    usuario = instance.participacion_asignada.id_usuario

    # Detectar si es creación o cambio de asignación
    if created:
        motivo = "asignado"
    else:
        # Verificamos si hubo cambio en la asignación usando el historial anterior
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.participacion_asignada != instance.participacion_asignada:
                motivo = "reasignado"
            else:
                return  # No hubo cambio, no notificar
        except sender.DoesNotExist:
            return

    subject = "Tarea asignada" if motivo == "asignado" else "Tarea reasignada"
    from_email = settings.EMAIL_HOST_USER
    to = [usuario.email]

    tarea_url = f"https://collabapp.com/proyectos/{instance.id_hu.proyecto.id}/hu/{instance.id_hu.id}/tareas/{instance.id}"
    text_content = (
        f"Se te ha {motivo} una tarea: '{instance.nombre_tarea}'.\n"
        f"Puedes verla en: {tarea_url}"
    )

    html_content = f"""
    <html>
    <body>
        <p>Se te ha <strong>{motivo}</strong> una tarea:</p>
        <p><strong>{instance.nombre_tarea}</strong></p>
        <p>Historia de usuario: <strong>{instance.id_hu.titulo}</strong></p>
        <p>Puedes verla en el siguiente enlace:</p>
        <a href="{tarea_url}">Ver tarea</a>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send()
    except Exception as e:
        print(f"Error al enviar email al desarrollador: {e}")