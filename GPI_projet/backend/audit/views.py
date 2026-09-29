from rest_framework import viewsets

from accounts.permissions import IsAdministrateur

from .models import ConnexionAudit, RapportAudit
from .serializers import ConnexionAuditSerializer, RapportAuditSerializer


class RapportAuditViewSet(viewsets.ModelViewSet):
    queryset = RapportAudit.objects.select_related("equipement").all()
    serializer_class = RapportAuditSerializer
    permission_classes = [IsAdministrateur]


class ConnexionAuditViewSet(viewsets.ModelViewSet):
    queryset = ConnexionAudit.objects.select_related(
        "equipement",
        "utilisateur",
    ).all()
    serializer_class = ConnexionAuditSerializer
    permission_classes = [IsAdministrateur]