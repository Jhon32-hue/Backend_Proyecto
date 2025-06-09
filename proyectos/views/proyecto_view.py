from rest_framework import viewsets, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from proyectos.models.proyecto import Proyecto
from proyectos.models.participacion import Participacion
from usuarios.models.rol import Rol
from usuarios.models.usuario import Usuario
from proyectos.serializers.proyecto_serializer import ProyectoSerializer

class ProyectoViewSet(viewsets.ModelViewSet):
    queryset = Proyecto.objects.all()
    serializer_class = ProyectoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #Esta función filtra proyectos del usuario actual
        return self.queryset.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        #Crea proyecto y asigna rol PMO automáticamente"""
        try:
            usuario_actual = Usuario.objects.get(id=self.request.user.id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario no válido.")
        
        proyecto = serializer.save(usuario=usuario_actual)
        rol_pmo, _ = Rol.objects.get_or_create(nombre_rol='PMO')
        
        Participacion.objects.create(
            id_usuario=usuario_actual,
            id_proyecto=proyecto,
            id_rol=rol_pmo,
            estado_participacion='activo'
        )

    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):  
        """Endpoint: GET /api/proyectos/estadisticas/"""
        queryset = self.get_queryset()  # Esto ya filtra por usuario
        
        return Response({
            'total_proyectos': queryset.count(),
            'proyectos_activos': queryset.filter(estado_proyecto='activo').count(),
            'proyectos_en_progreso': queryset.filter(estado_proyecto='en_progreso').count(),
            'proyectos_finalizados': queryset.filter(estado_proyecto='finalizado').count(),
            'ultimo_proyecto': {
            'id': queryset.last().id_proyecto if queryset.exists() else None,
            'nombre': queryset.last().nombre if queryset.exists() else None,
            'estado': queryset.last().estado_proyecto if queryset.exists() else None
        }
    })
    
    