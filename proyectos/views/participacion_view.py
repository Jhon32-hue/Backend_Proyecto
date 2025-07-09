from rest_framework import viewsets
from proyectos.models.participacion import Participacion
from proyectos.serializers.participacion_serializer import ParticipacionDetalleSerializer
from rest_framework.permissions import IsAuthenticated

class ParticipacionProyectoViewSet(viewsets.ModelViewSet):
    serializer_class = ParticipacionDetalleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        proyecto_id = self.request.query_params.get('proyecto')
        rol = self.request.query_params.get('rol')

        # ✅ Todos los usuarios autenticados pueden ver participaciones del proyecto si se pasa como parámetro
        if proyecto_id:
            queryset = Participacion.objects.filter(id_proyecto_id=proyecto_id)
        # 🧑‍💻 Si no hay proyecto, superuser ve todo
        elif user.is_superuser:
            queryset = Participacion.objects.all()
        # 🔐 Si no, solo ve sus propias participaciones
        else:
            queryset = Participacion.objects.filter(id_usuario=user)

        # 🔍 Filtro por rol si viene en query params
        if rol:
            queryset = queryset.filter(id_rol__nombre_rol__iexact=rol)

        print('🔎 Participaciones a retornar:')
        for p in queryset:
            print(f" - {p.id_participacion}: {p.id_usuario} → {p.id_usuario.nombre_completo if p.id_usuario else 'Sin usuario'}")

        return queryset
