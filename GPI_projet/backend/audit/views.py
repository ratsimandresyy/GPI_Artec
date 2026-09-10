from rest_framework import viewsets
from accounts.permissions import IsAdministrateurOrReadOnly

from .models import RapportAudit, ConnexionAudit
from .serializers import RapportAuditSerializer, ConnexionAuditSerializer

# Create your views here.

class RapportAuditViewSet(viewsets.ModelViewSet):
    queryset = RapportAudit.objects.select_related("equipement").all()
    serializer_class = RapportAuditSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class ConnexionAuditViewSet(viewsets.ModelViewSet):
    queryset = ConnexionAudit.objects.select_related("equipement, utilisateur").all()
    serializer_class = ConnexionAuditSerializer
    permission_classes = [IsAdministrateurOrReadOnly]