from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginSerializer

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import User;
from accounts.permissions import IsAdministrateurOrReadOnly, IsUserOrAdministrateur;
from .serializers import UserSerializer;
# Create your views here.

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

    def get_permissions(self):
        if self.action == "me":
            permission_classes = [IsUserOrAdministrateur]
        else:
            permission_classes = [IsAdministrateurOrReadOnly]
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=["get", "put"],
        url_path="me"
    )
    def me(self, request):
        """
        Permet à l'utilisateur connecté de consulter et modifier son propre profil.
        """
        if request.method == "GET":
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)

        elif request.method == "PUT":
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)