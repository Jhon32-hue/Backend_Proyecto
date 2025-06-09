from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from proyectos.models.proyecto import Proyecto
from proyectos.models.tarea import Tarea
from proyectos.models.hu import Historia_usuario
from actividades.models.historial import Historial_Actividad
from crum import get_current_user
from usuarios.models.usuario import Usuario

def obtener_usuario_valido():
    usuario = get_current_user()
    print("Usuario obtenido con crum:", usuario)

    if usuario is None or usuario.is_anonymous:
        # Puedes dejar un usuario de prueba o None si quieres
        try:
            usuario = Usuario.objects.first()
            print("Usuario fijo para test:", usuario)
            return usuario
        except Usuario.DoesNotExist:
            return None

    try:
        usuario = Usuario.objects.get(id=usuario.id)
        print("Usuario válido:", usuario)
        return usuario
    except Usuario.DoesNotExist:
        print("Usuario no existe en DB")
        return None

@receiver(post_save, sender=Proyecto)
def historial_proyecto(sender, instance, created, **kwargs):
    print("🔥 Signal ejecutado para Proyecto")
    usuario = obtener_usuario_valido()
    if usuario:
        accion = 'Creado' if created else 'Actualizado'
        Historial_Actividad.objects.create(
            usuario=usuario,
            proyecto=instance,
            accion_realizada=f'Proyecto {accion}: {instance.nombre}',
        )

@receiver(post_delete, sender=Proyecto)
def historial_eliminar_proyecto(sender, instance, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        Historial_Actividad.objects.create(
            usuario=usuario,
            proyecto=None,
            accion_realizada=f'Proyecto Eliminado: {instance.nombre}',
        )

@receiver(post_save, sender=Tarea)
def historial_tarea(sender, instance, created, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        accion = 'Creada' if created else 'Actualizada'
        Historial_Actividad.objects.create(
            usuario=usuario,
            tarea=instance,
            proyecto=instance.proyecto,
            accion_realizada=f'Tarea {accion}: {instance.nombre}',
        )

@receiver(post_delete, sender=Tarea)
def historial_eliminar_tarea(sender, instance, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        Historial_Actividad.objects.create(
            usuario=usuario,
            tarea=instance,
            proyecto=instance.proyecto,
            accion_realizada=f'Tarea Eliminada: {instance.nombre}',
        )

@receiver(post_save, sender=Historia_usuario)
def historial_hu(sender, instance, created, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        accion = 'Creada' if created else 'Actualizada'
        Historial_Actividad.objects.create(
            usuario=usuario,
            historia_usuario=instance,
            proyecto=instance.proyecto,
            accion_realizada=f'HU {accion}: {instance.titulo}',
        )

@receiver(post_delete, sender=Historia_usuario)
def historial_eliminar_hu(sender, instance, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        Historial_Actividad.objects.create(
            usuario=usuario,
            historia_usuario=instance,
            proyecto=instance.proyecto,
            accion_realizada=f'HU Eliminada: {instance.titulo}',
        )
