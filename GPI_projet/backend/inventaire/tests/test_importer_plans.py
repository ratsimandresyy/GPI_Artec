from django.test import TestCase

from inventaire.management.commands.importer_plans import (
    nom_image,
    numero_etage_depuis_nom,
)


class NumeroEtageDepuisNomTest(TestCase):
    """
    Tests de la deduction du niveau a partir du nom du fichier de plan.

    C'est la seule logique de la commande d'import qui merite un test :
    l'association fichier -> etage doit rester stricte, sans jamais
    deviner un niveau absent du nom.
    """

    def test_rez_de_chaussee(self):
        self.assertEqual(
            numero_etage_depuis_nom("247 200612 plan Rdc.pdf"),
            0,
        )

    def test_etage_positif(self):
        self.assertEqual(
            numero_etage_depuis_nom("247 200612 plan R+5.pdf"),
            5,
        )

    def test_etage_negatif(self):
        self.assertEqual(
            numero_etage_depuis_nom("247 200612 plan R-1.pdf"),
            -1,
        )

    def test_casse_et_espaces_ignores(self):
        self.assertEqual(
            numero_etage_depuis_nom("PLAN R + 2.pdf"),
            2,
        )

    def test_nom_sans_niveau(self):
        self.assertIsNone(numero_etage_depuis_nom("plan de masse.pdf"))
        self.assertIsNone(numero_etage_depuis_nom("scan001.pdf"))


class NomImageTest(TestCase):
    """Le nom de l'image ne depend que du numero d'etage."""

    def test_noms_de_fichiers(self):
        self.assertEqual(nom_image(0), "plan_etage_0.png")
        self.assertEqual(nom_image(3), "plan_etage_3.png")
        self.assertEqual(nom_image(-1), "plan_etage_-1.png")
