from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdministrateurOrReadOnly
from django.db import models

from .models import (
    Batiment,
    Etage,
    Salle,
    Equipement,
    Plan,
    Position,
)

from .serializers import (
    BatimentSerializer,
    EtageSerializer,
    SalleSerializer,
    EquipementSerializer,
    PlanSerializer,
    PositionSerializer,
    PositionDetailSerializer,
)
# Create your views here.

class BatimentViewSet(viewsets.ModelViewSet):
    queryset = Batiment.objects.all()
    serializer_class = BatimentSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class EtageViewSet(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class EquipementViewSet(viewsets.ModelViewSet):
    queryset = Equipement.objects.all()
    serializer_class = EquipementSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

    @action(
        detail = False,
        methods = ["get"],
        url_path = "rechercher",
    )
    def rechercher(self, request):
        terme = request.query_params.get("q", "").strip()

        if not terme :
            return Response(
                {
                    "detail": "Le paramètre 'q' est obligatoire." 
                },
                status = 400
            )

        equipements = self.get_queryset().filter(
            models.Q(nom__icontains=terme)
            | models.Q(numero_inventaire_icontains=terme)
        )

        serializer = self.get_serializer(
            equipements,
            many=True,
    )

        return Response(serializer.data)

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.select_related(
        "équipement",
        "plan",
    )
    serializer_class = PositionDetailSerializer
    permission_classes = [IsAdministrateurOrReadOnly]