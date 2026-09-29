from django.test import TestCase

from inventaire.models import Batiment, Etage, Salle, Equipement, Plan, Position
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

    def test_enregistrer_avec_une_salle_cree_une_position(self):
        """
        Enregistrer un materiel avec une salle le positionne
        automatiquement sur le plan de son etage, sans quoi
        il resterait invisible dans la vue Localisation.
        """

        Plan.objects.create(
            etage=self.etage,
            largeur=1000,
            hauteur=800,
        )

        serializer = EquipementSerializer(
            data={
                "nom": "PC Nouveau",
                "type": "ORDINATEUR",
                "numero_inventaire": "INV-100",
                "situation": "AFFECTE",
                "etat": "EN_SERVICE",
                "salle": self.salle.id,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        equipement = serializer.save()

        position = Position.objects.get(
            equipement=equipement
        )

        self.assertEqual(position.x, 500)
        self.assertEqual(position.y, 400)

    def test_modifier_la_salle_deplace_la_position(self):
        """
        Changer de salle deplace le materiel sur le plan
        de l'etage correspondant.
        """

        Plan.objects.create(
            etage=self.etage,
            largeur=1000,
            hauteur=800,
        )

        etage_2 = Etage.objects.create(
            batiment=self.batiment,
            numero=2,
            nom="Premier étage",
        )

        Plan.objects.create(etage=etage_2)

        salle_2 = Salle.objects.create(
            etage=etage_2,
            nom="Salle 201",
        )

        serializer = EquipementSerializer(
            instance=self.equipement,
            data={"salle": salle_2.id},
            partial=True,
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        equipement = serializer.save()

        position = Position.objects.get(
            equipement=equipement
        )

        self.assertEqual(position.plan.etage, etage_2)