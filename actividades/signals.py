# Imports comunes para que funcione la señal
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from proyectos.models.proyecto import Proyecto
from proyectos.models.tarea import Tarea
from proyectos.models.hu import Historia_usuario
from actividades.models.historial import Historial_Actividad
from proyectos.models.participacion import Participacion
from crum import get_current_user
from usuarios.models.usuario import Usuario

# Función para obtener el usuario responsable
def obtener_usuario_valido():
    usuario = get_current_user()
    print("Usuario obtenido con crum:", usuario)

    if usuario is None or usuario.is_anonymous:
        print("⚠️ Usuario no autenticado. No se registrará historial.")
        return None

    try:
        usuario = Usuario.objects.get(id=usuario.id)
        print("Usuario válido:", usuario)
        return usuario
    except Usuario.DoesNotExist:
        print("Usuario no existe en DB")
        return None

### 🔸 SECCIÓN: Proyecto
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

### 🔸 SECCIÓN: Pre-save Tarea para detectar cambio de estado
@receiver(pre_save, sender=Tarea)
def detectar_cambio_estado_tarea(sender, instance, **kwargs):
    if instance.pk:
        try:
            instancia_anterior = Tarea.objects.get(pk=instance.pk)
            instance._estado_anterior = instancia_anterior.estado_tarea
        except Tarea.DoesNotExist:
            instance._estado_anterior = None

@receiver(post_save, sender=Tarea)
def historial_tarea(sender, instance, created, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        if created:
            accion = f'Tarea Creada: {instance.titulo}'
        elif hasattr(instance, '_estado_anterior') and instance._estado_anterior != instance.estado_tarea:
            accion = f'Estado de Tarea cambiado: {instance._estado_anterior} → {instance.estado_tarea}'
        else:
            accion = f'Tarea Actualizada: {instance.titulo}'

        Historial_Actividad.objects.create(
            usuario=usuario,
            tarea=instance,
            proyecto=instance.id_hu.proyecto,
            accion_realizada=accion,
        )

@receiver(post_delete, sender=Tarea)
def historial_eliminar_tarea(sender, instance, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        Historial_Actividad.objects.create(
            usuario=usuario,
            tarea=instance,
            proyecto=instance.id_hu.proyecto,
            accion_realizada=f'Tarea Eliminada: {instance.titulo}',
        )

### 🔸 SECCIÓN: Pre-save HU para detectar cambio de estado o solicitud cierre
@receiver(pre_save, sender=Historia_usuario)
def detectar_cambio_estado_hu(sender, instance, **kwargs):
    if instance.pk:
        try:
            instancia_anterior = Historia_usuario.objects.get(pk=instance.pk)
            instance._estado_anterior = instancia_anterior.estado
        except Historia_usuario.DoesNotExist:
            instance._estado_anterior = None

@receiver(post_save, sender=Historia_usuario)
def historial_hu(sender, instance, created, **kwargs):
    usuario = obtener_usuario_valido()
    if usuario:
        if created:
            accion = f'HU Creada: {instance.titulo}'
        elif hasattr(instance, '_estado_anterior') and instance._estado_anterior != instance.estado:
            if instance.estado == 'Por aprobar':
                accion = f'Se solicitó cierre de la HU: {instance.titulo}'
            else:
                accion = f'Estado de HU cambiado: {instance._estado_anterior} → {instance.estado}'
        else:
            accion = f'HU Actualizada: {instance.titulo}'

        Historial_Actividad.objects.create(
            usuario=usuario,
            historia_usuario=instance,
            proyecto=instance.proyecto,
            accion_realizada=accion,
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

### 🔸 SECCIÓN: Cambio de Rol en Participación
@receiver(pre_save, sender=Participacion)
def guardar_rol_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instancia_anterior = Participacion.objects.get(pk=instance.pk)
            instance._rol_anterior = instancia_anterior.id_rol
        except Participacion.DoesNotExist:
            instance._rol_anterior = None

@receiver(post_save, sender=Participacion)
def historial_cambio_rol(sender, instance, created, **kwargs):
    if not created and hasattr(instance, '_rol_anterior'):
        rol_anterior = instance._rol_anterior
        rol_nuevo = instance.id_rol

        if rol_anterior and rol_nuevo and rol_anterior != rol_nuevo:
            usuario = obtener_usuario_valido()
            if usuario:
                Historial_Actividad.objects.create(
                    usuario=usuario,
                    proyecto=instance.id_proyecto,
                    accion_realizada=f'Rol cambiado en participación: {rol_anterior.nombre_rol} → {rol_nuevo.nombre_rol}',
                )
