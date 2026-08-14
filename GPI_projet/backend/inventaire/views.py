from rest_framework import viewsets

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
)
# Create your views here.

class BatimentViewSet(viewsets.ModelViewSet):
    queryset = Batiment.objects.all()
    serializer_class = BatimentSerializer

class EtageViewSet(viewsets.ModelViewSet):
    queryset = Etage.objects.all()
    serializer_class = EtageSerializer

class SalleViewSet(viewsets.ModelViewSet):
    queryset = Salle.objects.all()
    serializer_class = SalleSerializer

class EquipementViewSet(viewsets.ModelViewSet):
    queryset = Equipement.objects.all()
    serializer_class = EquipementSerializer

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer