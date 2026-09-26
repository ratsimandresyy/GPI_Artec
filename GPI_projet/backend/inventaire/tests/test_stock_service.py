from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.salle import Salle
from inventaire.models.plan import Plan
from inventaire.models.equipement import Equipement
from inventaire.models.position import Position 
from inventaire.services.stock_service import StockService

class StockServiceTest(TestCase):
    def setUp(self):
        self.batiment = Batiment.objects.create(
            nom ="Bâtiment TEST",
        )

        self.etage = Etage.objects.create(
            batiment = self.batiment,
            numero = 1,
            nom = "Rez-de-chaussée",
        )

        self.salle = Salle.objects.create(
            etage = self.etage,
            nom = "Salle TEST",
        )

        image = SimpleUploadedFile(
            "plan_test.png",
            b"fake-image-content",
            content_type="image/png",
        )

        self.plan = Plan.objects.create(
            etage = self.etage,
            image = image,
        )
        
        self.equipement = Equipement.objects.create(
            nom="PC-TEST-STOCK",
            type="ORDINATEUR",
            numero_inventaire="TEST-STOCK-001",
            numero_serie="SN-TEST-STOCK-001",
            situation="AFFECTE",
        )

    def test_transferer_vers_stock(self):
        StockService.transferer_vers_stock(
            self.equipement,
            condition_stock="OCCASION",
        )

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.etat,
            "EN_MAINTENANCE",
        )

        self.assertEqual(
            self.equipement.situation,
            "EN_STOCK",
        )

        self.assertIsNone(
            self.equipement.salle,
        )

    def test_transferer_vers_stock_supprime_position(self):

        Position.objects.create(
            equipement=self.equipement,
            plan=self.plan,
            x=150.0,
            y=250.0,
        )

        self.assertTrue(
             Position.objects.filter(
                 equipement = self.equipement
             ).exists()
         )

        StockService.transferer_vers_stock(
            self.equipement,
            condition_stock="OCCASION",
        )

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )

    def test_terminer_maintenance(self):
        self.equipement.situation = "EN_STOCK"
        self.equipement.etat = "EN_MAINTENANCE"
        self.equipement.salle = None
        self.equipement.save()

        StockService.terminer_maintenance(
            self.equipement
        )

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.etat,
            "EN_SERVICE",
        )

        self.assertEqual(
            self.equipement.situation,
            "EN_STOCK",
        )

        self.assertIsNone(
            self.equipement.salle,
        )

    def test_affecter_equipement(self):
        # Précondition :
        # l'équipement doit être en stock et en service.
        self.equipement.situation = "EN_STOCK"
        self.equipement.etat = "EN_SERVICE"
        self.equipement.salle = None
        self.equipement.save()

        StockService.affecter_equipement(
        self.equipement,
        self.salle,
        self.plan,
        150.0,
        250.0,
    )

        self.equipement.refresh_from_db()

        self.assertEqual(
        self.equipement.situation,
        "AFFECTE",
    )

        self.assertEqual(
        self.equipement.etat,
        "EN_SERVICE",
    )

        self.assertEqual(
        self.equipement.salle,
        self.salle,
    )

        position = Position.objects.get(
        equipement = self.equipement
    )

        self.assertEqual(position.plan, self.plan)
        self.assertEqual(position.x, 150.0)
        self.assertEqual(position.y, 250.0)