from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from inventaire.models.batiment import Batiment
from inventaire.models.equipement import Equipement
from inventaire.models.etage import Etage
from inventaire.models.salle import Salle


class EquipementQueriesTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.batiment = Batiment.objects.create(nom="Bâtiment requêtes")
        self.etage = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="RDC",
        )
        self.salle = Salle.objects.create(
            etage=self.etage,
            nom="Salle Q",
        )

    def _creer_equipements(self, nombre, decalage=0):
        for indice in range(nombre):
            Equipement.objects.create(
                nom=f"PC-Q-{decalage}-{indice}",
                type="ORDINATEUR",
                numero_inventaire=f"INV-Q-{decalage}-{indice}",
                situation="AFFECTE",
                etat="EN_SERVICE",
                salle=self.salle,
            )

    def test_liste_equipements_nombre_de_requetes_constant(self):
        self._creer_equipements(3)

        with CaptureQueriesContext(connection) as premier:
            response = self.client.get("/api/inventaire/equipements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        self._creer_equipements(5, decalage=10)

        with CaptureQueriesContext(connection) as second:
            response = self.client.get("/api/inventaire/equipements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 8)
        self.assertEqual(len(premier.captured_queries), len(second.captured_queries))
