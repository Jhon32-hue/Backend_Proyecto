from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from usuarios.serializers.usuario_serializer import Usuario_Serializer
from usuarios.models.usuario import Usuario
from django.utils import timezone

#Función personalizada para iniciar sesión
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
#Obtener el usuario y la contraseña que se ha enviado
    email_from_client= request.data.get('email')
    password_from_client= request.data.get('password')
    
#Se valida si el usuario está en la base de datos
    user = authenticate(email= email_from_client, password = password_from_client)

#Se genera el token si el la autenticacion fue un éxito
    if user and user.is_active:
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'email' : email_from_client,
                'nombre_completo' : user.nombre_completo,
                'user_id' : user.id,
                'estado_cuenta' : user.estado_cuenta,
                'refresh' : str(refresh),
                'token' : str(refresh.access_token),
            },
            status.HTTP_200_OK
        )
    else:
        return Response(
            {
                'error' : "Credenciales invalidas"
            },
            status.HTTP_401_UNAUTHORIZED
        )
    

@api_view(['POST'])
@permission_classes([AllowAny])
def google_auth_callback_view(request):
    email = request.data.get('email')
    nombre = request.data.get('nombre_completo')

    if not email or not nombre:
        return Response({'error': 'Faltan datos necesarios'}, status=400)

    try:
        user = Usuario.objects.get(email=email)
        if user.nombre_completo != nombre:
            user.nombre_completo = nombre
            user.save(update_fields=['nombre_completo'])
    except Usuario.DoesNotExist:
        user = Usuario.objects.create_user(email=email, nombre_completo=nombre)

    user.ultima_conexion = timezone.now()
    user.save(update_fields=['ultima_conexion'])

    refresh = RefreshToken.for_user(user)
    
    return Response({
        'email': user.email,
        'nombre_completo': user.nombre_completo,
        'user_id': user.id,
        'estado_cuenta': user.estado_cuenta,
        'refresh': str(refresh),
        'token': str(refresh.access_token),
    })
