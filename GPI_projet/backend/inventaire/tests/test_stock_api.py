from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.salle import Salle
from inventaire.models.plan import Plan
from inventaire.models.equipement import Equipement
from inventaire.models.position import Position


class StockAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Administrateur nécessaire pour les opérations d'écriture.
        self.admin = User.objects.create_user(
            username="admin_test",
            password="admin123",
            role=User.Role.ADMIN,
        )

        self.client.force_authenticate(user=self.admin)

        self.batiment = Batiment.objects.create(
            nom="Bâtiment A"
        )

        self.etage = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="Rez-de-chaussée",
        )

        self.salle = Salle.objects.create(
            etage=self.etage,
            nom="Salle 101",
        )

        self.plan = Plan.objects.create(
            etage=self.etage,
            largeur=1000,
            hauteur=800,
        )

        self.equipement = Equipement.objects.create(
            nom="PC-001",
            numero_inventaire="INV-001",
            situation="AFFECTE",
            etat="EN_SERVICE",
            salle=self.salle,
        )

    def test_transferer_vers_stock(self):
        """
        Vérifie qu'un équipement affecté peut être transféré
        vers le stock avec une condition valide.
        """

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/transferer-vers-stock/",
            {
                "condition_stock": "OCCASION",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.situation,
            "EN_STOCK",
        )

        self.assertEqual(
            self.equipement.condition_stock,
            "OCCASION",
        )

        self.assertEqual(
            self.equipement.etat,
            "EN_MAINTENANCE",
        )

        self.assertIsNone(
            self.equipement.salle,
        )

    def test_transferer_vers_stock_supprime_position(self):
        """
        Vérifie que le transfert vers le stock supprime
        la position graphique de l'équipement.
        """

        Position.objects.create(
            equipement=self.equipement,
            plan=self.plan,
            x=200,
            y=300,
        )

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/transferer-vers-stock/",
            {
                "condition_stock": "OCCASION",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )

    def test_transferer_vers_stock_sans_condition(self):
        """
        Vérifie que la condition du matériel est obligatoire.
        """

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/transferer-vers-stock/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "condition",
            response.data["detail"].lower(),
        )

    def test_transferer_vers_stock_condition_invalide(self):
        """
        Vérifie qu'une condition inconnue est refusée.
        """

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/transferer-vers-stock/",
            {
                "condition_stock": "MAUVAIS",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_terminer_maintenance(self):
        """
        Vérifie qu'un équipement en maintenance peut
        terminer sa maintenance.
        """

        self.equipement.situation = "EN_STOCK"
        self.equipement.etat = "EN_MAINTENANCE"
        self.equipement.condition_stock = "OCCASION"
        self.equipement.salle = None

        self.equipement.save()

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/terminer-maintenance/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.situation,
            "EN_STOCK",
        )

        self.assertEqual(
            self.equipement.etat,
            "EN_SERVICE",
        )

    def test_affecter_equipement(self):
        """
        Vérifie qu'un équipement en stock et en service
        peut être réaffecté à une salle et localisé.
        """

        self.equipement.situation = "EN_STOCK"
        self.equipement.etat = "EN_SERVICE"
        self.equipement.condition_stock = "OCCASION"
        self.equipement.salle = None

        self.equipement.save()

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/affecter/",
            {
                "salle": self.salle.id,
                "plan": self.plan.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.situation,
            "AFFECTE",
        )

        self.assertEqual(
            self.equipement.etat,
            "EN_SERVICE",
        )

        self.assertIsNone(
            self.equipement.condition_stock,
        )

        self.assertEqual(
            self.equipement.salle,
            self.salle,
        )

        position = Position.objects.get(
            equipement=self.equipement
        )

        self.assertEqual(position.plan, self.plan)
        self.assertEqual(position.x, 200)
        self.assertEqual(position.y, 300)

    def test_affecter_equipement_non_en_service(self):
        """
        Vérifie qu'un équipement encore en maintenance
        ne peut pas être affecté.
        """

        self.equipement.situation = "EN_STOCK"
        self.equipement.etat = "EN_MAINTENANCE"
        self.equipement.condition_stock = "OCCASION"
        self.equipement.salle = None

        self.equipement.save()

        response = self.client.post(
            f"/api/inventaire/equipements/"
            f"{self.equipement.id}/affecter/",
            {
                "salle": self.salle.id,
                "plan": self.plan.id,
                "x": 200,
                "y": 300,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        self.assertIn(
            "service",
            response.data["detail"].lower(),
        )