from rest_framework import generics, permissions
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.rol import Rol
from proyectos.serializers.proyecto_serializer import ProyectoSerializer


class CrearProyectoView(generics.CreateAPIView):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated] 

    #Crear proyecto con usuario autenticado
    def perform_create(self, serializer):
        proyecto = serializer.save(usuario=self.request.user)

        # Buscar el rol PMO
        rol_pmo = Rol.objects.get(nombre_rol='PMO')
        # Crear la participación automáticamente
        Participacion.objects.create(
            usuario=self.request.user,
            proyecto=proyecto,
            rol=rol_pmo,
            estado_participacion='Felicidades, ha creado un proyecto y ahora es el PMO asignado'  
        )
