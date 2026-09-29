from django.test import TestCase
from rest_framework.test import APIClient

from inventaire.models.equipement import Equipement
from inventaire.services.recherche_service import RechercheService


class RechercheServiceTest(TestCase):

    def setUp(self):
        self.pc_du_bureau = Equipement.objects.create(
            nom="PC-BUREAU-01",
            type="ORDINATEUR",
            numero_inventaire="INV-0001",
            situation="AFFECTE",
            etat="EN_SERVICE",
        )

        self.portable = Equipement.objects.create(
            nom="LAPTOP-SALLE-02",
            type="ORDINATEUR",
            numero_inventaire="INV-0002",
            situation="AFFECTE",
            etat="EN_SERVICE",
        )

    def test_recherche_sur_le_nom(self):
        resultat = RechercheService.rechercher_equipements(
            Equipement.objects.all(),
            "bureau",
        )

        self.assertEqual(list(resultat), [self.pc_du_bureau])

    def test_recherche_sur_le_numero_inventaire(self):
        resultat = RechercheService.rechercher_equipements(
            Equipement.objects.all(),
            "0002",
        )

        self.assertEqual(list(resultat), [self.portable])

    def test_les_espaces_sont_ignores(self):
        resultat = RechercheService.rechercher_equipements(
            Equipement.objects.all(),
            "   laptop   ",
        )

        self.assertEqual(list(resultat), [self.portable])

    def test_un_terme_vide_est_refuse(self):
        with self.assertRaises(ValueError):
            RechercheService.rechercher_equipements(
                Equipement.objects.all(),
                "   ",
            )

    def test_un_terme_absent_est_refuse(self):
        with self.assertRaises(ValueError):
            RechercheService.rechercher_equipements(
                Equipement.objects.all(),
                "",
            )


class RechercheApiTest(TestCase):
    """Le mode visiteur peut rechercher les equipements."""

    def setUp(self):
        self.client = APIClient()

        self.equipement = Equipement.objects.create(
            nom="PC-RECHERCHE-01",
            type="ORDINATEUR",
            numero_inventaire="INV-RECH-01",
            situation="AFFECTE",
            etat="EN_SERVICE",
        )

    def test_visiteur_peut_rechercher(self):
        response = self.client.get(
            "/api/inventaire/equipements/rechercher/",
            {"q": "RECHERCHE"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.equipement.id)

    def test_recherche_sans_terme_renvoie_une_erreur(self):
        response = self.client.get("/api/inventaire/equipements/rechercher/")

        self.assertEqual(response.status_code, 400)

    def test_recherche_vide_renvoie_une_liste_vide(self):
        response = self.client.get(
            "/api/inventaire/equipements/rechercher/",
            {"q": "introuvable"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
