from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny

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
                'refresh' : str(refresh),
                'token' : str(refresh.access_token)
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