from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from usuarios.models.rol import Rol

class RolListarView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            return Response({'detail': 'No autorizado.'}, status=status.HTTP_403_FORBIDDEN)

        roles = [
            {
                'id_rol': rol.id_rol,
                'clave': rol.nombre_rol,
                'nombre': rol.get_nombre_rol_display()
            }
            for rol in Rol.objects.all()
        ]

        return Response({'roles': roles}, status=status.HTTP_200_OK)
