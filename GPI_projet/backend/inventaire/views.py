from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import IsAdministrateurOrReadOnly, IsUserOrAdministrateur
from django.db import models

from .models import (
    Batiment,
    Etage,
    Salle,
    Equipement,
    Plan,
    Position,
    TicketPanne
)

from .serializers import (
    BatimentSerializer,
    EtageSerializer,
    SalleSerializer,
    EquipementSerializer,
    PlanSerializer,
    PositionSerializer,
    PositionDetailSerializer,
    TicketPanneSerializer
)

from .services.panne_service import PanneService
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
            | models.Q(numero_inventaire__icontains=terme)
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
        "equipement",
        "plan",
    )
    serializer_class = PositionDetailSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

class TicketPanneViewSet(viewsets.ModelViewSet):
    queryset = TicketPanne.objects.select_related("equipement").all()
    serializer_class = TicketPanneSerializer

    def get_permissions(self):
        if self.action in ("prendre_en_charge", "resoudre"):
            permission_classes = [IsAdministrateurOrReadOnly]
        else:
            permission_classes = [IsUserOrAdministrateur]

        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "La modification directe d'un ticket n'est pas autorisée."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )

    def destroy(self, request, *args, **kwargs):
        return Response(
            {
                "detail": "La suppression d'un ticket n'est pas autorisée."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
    )

    def create(self, request, *args, **kwargs):

        equipement_id = request.data.get("equipement")
        description = request.data.get("description")

        #vérification de la présence des données nécessaires
        if not equipement_id or not description:
            return Response(
                {
                    "detail": "L'équipement et la description sont obligatoires."
                },
                status = status.HTTP_400_BAD_REQUEST,
            )

        # Recherche de l'équipement concerné
        try:
            equipement = Equipement.objects.get(pk=equipement_id)
        except Equipement.DoesNotExist:
            return Response(
                {
                    "détail": "L'équipement demandé n'existe pas."
                },
                status = status.HTTP_404_NOT_FOUND,
            )

        #la logique métier es centralisé dans le service
        ticket = PanneService.declarer_panne(equipement=equipement, description=description)

        #Sérialisation du ticket créé
        serializer = self.get_serializer(ticket)

        return Response(
            serializer.data,
            status = status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="prendre-en-charge",
    )

    def prendre_en_charge(self, request, pk=None):
        ticket = self.get_object()

        try:
            ticket = PanneService.prendre_en_charge(ticket)
        except ValueError as e:
            return Response(
                {"détail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(ticket)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="resoudre",
    )

    def resoudre(self, request, pk=None):
        ticket = self.get_object()

        commentaire = request.data.get(
            "commentaire_resolution"
        )

        if not commentaire:
            return Response(
                {
                    "détail": (
                        "Le commentaire de résolution"
                        "est obligatoire."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ticket=PanneService.resoudre_ticket(
                ticket=ticket,
                commentaire_resolution=commentaire,
            )
        except ValueError as e:
            return Response(
                {"détail" : str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(ticket)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )