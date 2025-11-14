from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from .models import Usuario, Visitante
from .serializers import (
    UsuarioSerializer,
    LoginSerializer,
    VisitanteSerializer,
)

class UsuarioViewSet(viewsets.ModelViewSet):

    # ViewSet para gestión de usuarios
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action in ['login', 'create']:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def login(self, request):

        # Endpoint para login de usuarios
        serializers = LoginSerializer(data=request.data, context={'request': request})
        serializers.is_valid(raise_exception=True)

        usuario = serializers.validated_data['usuario']
        login(request, usuario)

        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=usuario)

        return Response({
            'token': token.key,
            'usuario': UsuarioSerializer(usuario).data,
            'mensaje': 'Login exitoso'
        })
    
    @action(detail=False, methods=['post'])
    def logout(self, request):

        # Endpoint para logout
        try:
            request.user.auth_token.delete()
        except:
            pass
        logout(request)
        return Response({'mensaje': 'Logout exitoso'})
    
    @action (detail=False, methods=['get'])
    def perfil (self, request):

        # Obtener perfil del usuario actual
        serializers = self.get_serializer(request.user)
        return Response(serializers.data)
    
    @action (detail=False, methods=['get'])
    def por_rol (self, request):

        # Filtrar usuarios por rol
        rol = request.query_params.get('rol', None)
        if rol:
            usuarios = self.queryset.filter(rol=rol, activo=True)
            serializers = self.get_serializer(usuarios, many=True)
            return Response(serializers.data)
        return Response({'error': 'Parámetro rol requerido'}, status=status.HTTP_400_BAD_REQUEST)

class VisitanteViewSet(viewsets.ModelViewSet):

    # ViewSet para gestión de visitantes
    queryset = Visitante.objects.all()
    serializer_class = VisitanteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @action(detail=False, methods=['get'])
    def activos(self, request):

        # Obtener visitantes activos (sin hora de salida)
        visitantes = self.queryset.filter(hora_salida__isnull=True, activo=True)
        serializer = self.get_serializer(visitantes, many=True)
        return Response(serializer.data)