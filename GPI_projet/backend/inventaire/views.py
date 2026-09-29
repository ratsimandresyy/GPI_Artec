from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response

from accounts.permissions import IsAdministrateur, IsAdministrateurOrReadOnly
from accounts.throttles import TicketCreateRateThrottle

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
    EquipementPublicSerializer,
    PlanSerializer,
    PositionSerializer,
    PositionDetailSerializer,
    TicketPanneSerializer
)

from .services.panne_service import PanneService
from .services.recherche_service import RechercheService
from .services.stock_service import StockService
from .services.localisation_service import LocalisationService

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
    queryset = Equipement.objects.select_related("salle").all()
    serializer_class = EquipementSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

    def _est_administrateur(self) -> bool:
        """
        Delegue la verification du role a IsAdministrateur.

        La regle "qui est administrateur" reste definie a un seul
        endroit (accounts/permissions.py) et n'est pas dupliquee ici.
        """
        if self.request is None:
            return False

        return IsAdministrateur().has_permission(self.request, self)

    def get_serializer_class(self):
        """
        Le visiteur lit une representation reduite de l'equipement ;
        l'administrateur conserve la representation complete, y
        compris sur les endpoints de lecture qu'il utilise pour son
        travail (tableau de parc, fiche detaillee).
        """
        if self.request.method in SAFE_METHODS and not self._est_administrateur():
            return EquipementPublicSerializer

        return EquipementSerializer

    @action(
        detail = False,
        methods = ["get"],
        url_path = "rechercher",
    )
    def rechercher(self, request):
        try:
            equipements = RechercheService.rechercher_equipements(
                queryset = self.get_queryset(),
                terme = request.query_params.get("q", ""),
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status = status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            equipements,
            many=True,
        )

        return Response(serializer.data)

    @action(
        detail=True,
        methods=["post"],
        url_path="transferer-vers-stock",
    )
    def transferer_vers_stock(self, request, pk=None):
        equipement = self.get_object()

        condition_stock = request.data.get("condition_stock")

        if not condition_stock:
            return Response(
                {
                    "detail": (
                        "La condition du matériel est obligatoire."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            equipement = StockService.transferer_vers_stock(
                equipement=equipement,
                condition_stock=condition_stock,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(equipement)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="terminer-maintenance",
    )
    def terminer_maintenance(self, request, pk=None):
        equipement = self.get_object()

        try:
            equipement = StockService.terminer_maintenance(
                equipement=equipement,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(equipement)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="affecter",
    )
    def affecter(self, request, pk=None):
        equipement = self.get_object()

        salle_id = request.data.get("salle")
        plan_id = request.data.get("plan")
        x = request.data.get("x")
        y = request.data.get("y")

        if not all([
            salle_id,
            plan_id,
            x is not None,
            y is not None,
        ]):
            return Response(
                {
                    "detail": (
                        "La salle, le plan, les coordonnées X "
                        "et Y sont obligatoires."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            salle = Salle.objects.get(pk=salle_id)
        except Salle.DoesNotExist:
            return Response(
                {
                    "detail": "La salle demandée n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            plan = Plan.objects.get(pk=plan_id)
        except Plan.DoesNotExist:
            return Response(
                {
                    "detail": "Le plan demandé n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            equipement = StockService.affecter_equipement(
                equipement=equipement,
                salle=salle,
                plan=plan,
                x=x,
                y=y,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(equipement)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    permission_classes = [IsAdministrateurOrReadOnly]


class PositionViewSet(viewsets.ModelViewSet):
    """
    API de gestion des positions des équipements.

    Les règles métier de localisation et de déplacement
    sont centralisées dans LocalisationService.
    """

    queryset = Position.objects.select_related(
        "equipement",
        "plan",
        "equipement__salle",
    )

    serializer_class = PositionDetailSerializer
    permission_classes = [IsAdministrateurOrReadOnly]

    @action(
        detail=False,
        methods=["post"],
        url_path="localiser",
    )
    def localiser(self, request):
        """
        Localise un équipement sur un plan.

        Exemple de requête :

        {
            "equipement": 1,
            "plan": 2,
            "x": 200,
            "y": 300
        }
        """

        equipement_id = request.data.get("equipement")
        plan_id = request.data.get("plan")
        x = request.data.get("x")
        y = request.data.get("y")

        # Vérification des données obligatoires.
        if None in (equipement_id, plan_id, x, y):
            return Response(
                {
                    "detail": (
                        "L'équipement, le plan, les coordonnées X "
                        "et Y sont obligatoires."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Recherche de l'équipement.
        try:
            equipement = Equipement.objects.get(
                pk=equipement_id
            )
        except Equipement.DoesNotExist:
            return Response(
                {
                    "detail": "L'équipement demandé n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Recherche du plan.
        try:
            plan = Plan.objects.get(
                pk=plan_id
            )
        except Plan.DoesNotExist:
            return Response(
                {
                    "detail": "Le plan demandé n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Un équipement doit être affecté à une salle.
        if equipement.salle is None:
            return Response(
                {
                    "detail": (
                        "L'équipement doit être affecté "
                        "à une salle avant sa localisation."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            position = LocalisationService.localiser_equipement(
                equipement=equipement,
                salle=equipement.salle,
                plan=plan,
                x=float(x),
                y=float(y),
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(position)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="deplacer",
    )
    def deplacer(self, request, pk=None):
        """
        Déplace un équipement déjà localisé.

        Exemple :

        POST /api/inventaire/positions/1/deplacer/

        {
            "plan": 2,
            "x": 500,
            "y": 600
        }
        """

        position = self.get_object()

        plan_id = request.data.get("plan")
        x = request.data.get("x")
        y = request.data.get("y")

        if None in (plan_id, x, y):
            return Response(
                {
                    "detail": (
                        "Le plan, les coordonnées X et Y "
                        "sont obligatoires."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            plan = Plan.objects.get(
                pk=plan_id
            )
        except Plan.DoesNotExist:
            return Response(
                {
                    "detail": "Le plan demandé n'existe pas."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            position = LocalisationService.deplacer_equipement(
                equipement=position.equipement,
                plan=plan,
                x=float(x),
                y=float(y),
            )

        except ValueError as error:
            return Response(
                {
                    "detail": str(error)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(position)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        """
        Retire la localisation graphique d'un équipement.
        """

        position = self.get_object()

        LocalisationService.retirer_localisation(
            position.equipement
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def create(self, request, *args, **kwargs):
        """
        La creation d'une position passe par LocalisationService.

        RG-P06, RG-P07 et RG-P08 ne doivent pas pouvoir etre contournees
        par une creation directe sur /positions/ : la regle metier reste
        centralisee dans le service.
        """
        return self.localiser(request)

class TicketPanneViewSet(viewsets.ModelViewSet):
    queryset = TicketPanne.objects.select_related("equipement").all()
    serializer_class = TicketPanneSerializer
    permission_classes = [IsAdministrateur]

    TYPES_SIGNALEMENT = ("MAINTENANCE", "RECLAMATION")
    PRIORITES_SIGNALEMENT = ("BASSE", "NORMALE", "HAUTE")

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        return [IsAdministrateur()]

    def get_throttles(self):
        if self.action == "create":
            return [TicketCreateRateThrottle()]
        return []

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
        titre = request.data.get("titre", "")
        description = request.data.get("description")
        type_ticket = request.data.get("type", "MAINTENANCE")
        priorite = request.data.get("priorite", "NORMALE")

        if not equipement_id or not description:
            return Response(
                {
                    "detail": (
                        "L'équipement et la description sont obligatoires."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if type_ticket not in self.TYPES_SIGNALEMENT:
            return Response(
                {
                    "detail": (
                        "Le type de signalement doit être "
                        "MAINTENANCE ou RECLAMATION."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if priorite == "CRITIQUE":
            return Response(
                {
                    "detail": (
                        "La priorité CRITIQUE est réservée "
                        "à l'administration."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if priorite not in self.PRIORITES_SIGNALEMENT:
            return Response(
                {
                    "detail": (
                        "Priorité invalide. Valeurs autorisées "
                        "pour un signalement : BASSE, NORMALE, HAUTE."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            equipement = Equipement.objects.get(pk=equipement_id)
        except Equipement.DoesNotExist:
            return Response(
                {"detail": "L'équipement demandé n'existe pas."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            ticket = PanneService.declarer_panne(
                equipement=equipement,
                titre=titre,
                description=description,
                type=type_ticket,
                priorite=priorite,
            )
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(ticket)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
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
                {"detail": str(e)},
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
                    "detail": (
                        "Le commentaire de résolution "
                        "est obligatoire."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        #L'etat final du materiel depend du diagnostic
        #(diagramme d'activite) : EN_SERVICE si le materiel est repare,
        #HORS_SERVICE sinon.
        etat_final = request.data.get(
            "etat_final",
            "EN_SERVICE",
        )

        try:
            ticket = PanneService.resoudre_ticket(
                ticket=ticket,
                commentaire_resolution=commentaire,
                etat_final=etat_final,
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
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
        url_path="qualifier",
    )

    def qualifier(self, request, pk=None):
        """
        Qualifie un ticket : type et/ou priorite.

        Diagramme d'activite : "Qualifier le ticket : definir le type,
        definir la priorite". La modification directe du ticket reste
        interdite (les transitions de statut passent par les actions
        prendre-en-charge et resoudre).
        """
        ticket = self.get_object()

        try:
            ticket = PanneService.qualifier_ticket(
                ticket=ticket,
                type=request.data.get("type"),
                priorite=request.data.get("priorite"),
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(ticket)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )