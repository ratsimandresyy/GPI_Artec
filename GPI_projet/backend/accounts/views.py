from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer

from rest_framework import viewsets;
from accounts.models import User;
from accounts.permissions import IsAdministrateurOrReadOnly;
from .serializers import UserSerializer;
# Create your views here.

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrateurOrReadOnly]