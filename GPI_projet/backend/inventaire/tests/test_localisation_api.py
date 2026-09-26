from django.test import TestCase
from rest_framework.test import APIClient

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.salle import Salle
from inventaire.models.plan import Plan
from inventaire.models.equipement import Equipement
from inventaire.models.position import Position
from accounts.models import User

class LocalisationAPITest(TestCase):
    """
    Tests de l'API de localisation des équipements.
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
    username="admin_test",
    password="admin123",
    role=User.Role.ADMIN,
)

        self.client.force_authenticate(user=self.admin)

        # Bâtiment
        self.batiment = Batiment.objects.create(
            nom="Bâtiment A"
        )

        # Étages
        self.etage_1 = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="Rez-de-chaussée"
        )

        self.etage_2 = Etage.objects.create(
            batiment=self.batiment,
            numero=2,
            nom="Premier étage"
        )

        # Plans
        self.plan_1 = Plan.objects.create(
            etage=self.etage_1,
            largeur=1000,
            hauteur=800
        )

        self.plan_2 = Plan.objects.create(
            etage=self.etage_2,
            largeur=1000,
            hauteur=800
        )

        # Salles
        self.salle_1 = Salle.objects.create(
            etage=self.etage_1,
            nom="Salle 101"
        )

        self.salle_2 = Salle.objects.create(
            etage=self.etage_2,
            nom="Salle 201"
        )

        # Équipement
        self.equipement = Equipement.objects.create(
            nom="PC-001",
            numero_inventaire="INV-001",
            situation="AFFECTE",
            salle=self.salle_1,
        )

    def test_localiser_equipement(self):
        """
        L'API permet de localiser un équipement affecté.
        """

        response = self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(
            Position.objects.filter(
                equipement=self.equipement
            ).count(),
            1
        )

        position = Position.objects.get(
            equipement=self.equipement
        )

        self.assertEqual(position.plan, self.plan_1)
        self.assertEqual(position.x, 200)
        self.assertEqual(position.y, 300)

    def test_localiser_equipement_hors_limites(self):
        """
        L'API refuse une position située hors du plan.
        """

        response = self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 1001,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "dépasse",
            response.data["detail"]
        )

    def test_localiser_equipement_en_stock(self):
        """
        L'API refuse de localiser un équipement en stock.
        """

        self.equipement.situation = "EN_STOCK"
        self.equipement.save()

        response = self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "affecté",
            response.data["detail"]
        )

    def test_deplacer_equipement(self):
        """
        L'API permet de déplacer un équipement déjà localisé.
        """

        # Localisation initiale
        self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        position = Position.objects.get(
            equipement=self.equipement
        )

        response = self.client.post(
            f"/api/inventaire/positions/{position.id}/deplacer/",
            {
                "plan": self.plan_1.id,
                "x": 500,
                "y": 600,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        position.refresh_from_db()

        self.assertEqual(position.x, 500)
        self.assertEqual(position.y, 600)

    def test_deplacement_vers_autre_etage(self):
        """
        L'API refuse de déplacer un équipement
        vers un plan d'un autre étage.
        """

        self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        position = Position.objects.get(
            equipement=self.equipement
        )

        response = self.client.post(
            f"/api/inventaire/positions/{position.id}/deplacer/",
            {
                "plan": self.plan_2.id,
                "x": 500,
                "y": 600,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_supprimer_localisation(self):
        """
        L'API permet de supprimer la localisation
        graphique d'un équipement.
        """

        self.client.post(
            "/api/inventaire/positions/localiser/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        position = Position.objects.get(
            equipement=self.equipement
        )

        response = self.client.delete(
            f"/api/inventaire/positions/{position.id}/"
        )

        self.assertEqual(response.status_code, 204)

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )

    def test_creation_directe_de_position_passe_par_le_service(self):
        """
        RG-P06 : la création directe d'une position ne doit pas permettre
        de localiser un matériel qui n'est pas affecté.
        """
        self.equipement.situation = "EN_STOCK"
        self.equipement.condition_stock = "NEUF"
        self.equipement.save()

        response = self.client.post(
            "/api/inventaire/positions/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )

    def test_creation_directe_hors_limites_du_plan_refusee(self):
        """
        RG-P07 : les coordonnées doivent rester dans les limites du plan,
        y compris par une création directe.
        """
        response = self.client.post(
            "/api/inventaire/positions/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 5000,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(Position.objects.exists())

    def test_creation_directe_dans_un_autre_etage_refusee(self):
        """
        RG-P08 : la salle de l'équipement et le plan utilisé doivent
        appartenir au même étage.
        """
        response = self.client.post(
            "/api/inventaire/positions/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_2.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertFalse(Position.objects.exists())

    def test_creation_directe_valide_est_acceptee(self):
        """
        La création directe reste possible lorsque les règles métier
        sont respectées (elle délègue à LocalisationService).
        """
        response = self.client.post(
            "/api/inventaire/positions/",
            {
                "equipement": self.equipement.id,
                "plan": self.plan_1.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Position.objects.count(), 1)