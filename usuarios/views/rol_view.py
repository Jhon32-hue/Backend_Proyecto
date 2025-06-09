from rest_framework import viewsets
from usuarios.models.rol import Rol
from usuarios.serializers.rol_serializer import Rol_Serializer
from rest_framework.permissions import IsAuthenticated

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = Rol_Serializer
    permission_classes = [IsAuthenticated]
