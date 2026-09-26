from django.test import TestCase

from inventaire.models import Batiment, Etage, Salle, Equipement
from inventaire.serializers import EquipementSerializer


class EquipementSerializerTest(TestCase):

    def setUp(self):
        self.batiment = Batiment.objects.create(
            nom="Bâtiment Test"
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

        self.equipement = Equipement.objects.create(
            nom="PC Test",
            numero_inventaire="INV-001",
            situation="AFFECTE",
            etat="EN_SERVICE",
            salle=self.salle,
        )

    def test_equipement_affecte_avec_salle_est_valide(self):
        serializer = EquipementSerializer(
            instance=self.equipement,
            data={
                "nom": "PC Test modifié",
                "numero_inventaire": "INV-001",
                "situation": "AFFECTE",
                "etat": "EN_SERVICE",
                "salle": self.salle.id,
            },
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_equipement_en_stock_avec_salle_est_refuse(self):
        serializer = EquipementSerializer(
            instance=self.equipement,
            data={
                "situation": "EN_STOCK",
                "salle": self.salle.id,
                "condition_stock": "OCCASION",
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("salle", serializer.errors)