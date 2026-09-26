"""
Tests du mapping des données WinAudit vers le modèle GPI.
"""

from django.test import SimpleTestCase

from audit.mapping import WinAuditMapper
from audit.models import RapportAudit
from inventaire.models.equipement import Equipement


class WinAuditMapperTest(SimpleTestCase):
    """
    Le mapper ne doit produire que des champs réellement déclarés
    sur les modèles (garde-fou contre une faute de frappe du type
    "sitution" au lieu de "situation").
    """

    def setUp(self):
        self.donnees = {
            "Résumé du Système": {
                "Computer Name": "AD1",
                "Asset Tag": "INV-2021-001",
                "Serial Number": "SERIE-0001",
                "Manufacturer": "Dell Inc.",
                "Model": "OptiPlex 3070",
                "Operating System": "Windows 10 Professionnel",
                "Processor Description": "Intel(R) Core(TM) i5-9400",
                "Total Memory": "8,00 Go",
                "Total Hard Drive": "256,00 Go",
                "BIOS Version": "1.2.3",
            }
        }
        self.mapper = WinAuditMapper(self.donnees, None)

    @staticmethod
    def _noms_de_champs(modele):
        return {champ.name for champ in modele._meta.get_fields()}

    def test_les_cles_equipement_existent_sur_le_modele(self):
        cles = set(self.mapper.map_equipement())

        inconnues = cles - self._noms_de_champs(Equipement)

        self.assertEqual(
            inconnues,
            set(),
            f"Champs inexistants sur Equipement : {sorted(inconnues)}",
        )

    def test_les_cles_rapport_existent_sur_le_modele(self):
        cles = set(self.mapper.map_rapport_audit())
        champs = self._noms_de_champs(RapportAudit)

        inconnues = cles - champs

        self.assertEqual(
            inconnues,
            set(),
            f"Champs inexistants sur RapportAudit : {sorted(inconnues)}",
        )

    def test_equipement_reprend_les_valeurs_de_la_collecte(self):
        equipement = self.mapper.map_equipement()

        self.assertEqual(equipement["nom"], "AD1")
        self.assertEqual(equipement["type"], "ORDINATEUR")
        self.assertEqual(equipement["numero_inventaire"], "INV-2021-001")
        self.assertEqual(equipement["numero_serie"], "SERIE-0001")
        self.assertEqual(equipement["fabricant"], "Dell Inc.")
        self.assertEqual(equipement["modele"], "OptiPlex 3070")

    def test_la_collecte_ne_place_jamais_un_materiel_en_stock(self):
        """
        RG-E04 / RG-E08 : un matériel collecté est affecté et ne
        possède donc aucune condition de stock.
        """
        equipement = self.mapper.map_equipement()

        self.assertEqual(equipement["situation"], "AFFECTE")
        self.assertEqual(equipement["etat"], "EN_SERVICE")
        self.assertIsNone(equipement["salle"])
        self.assertNotIn("condition_stock", equipement)

    def test_une_valeur_absente_devient_une_chaine_vide(self):
        mapper = WinAuditMapper({"Résumé du Système": {}}, None)

        equipement = mapper.map_equipement()

        self.assertEqual(equipement["nom"], "")
        self.assertEqual(equipement["numero_inventaire"], "")

    def test_un_numero_de_serie_absent_devient_none(self):
        """
        RG-E03 : sans numéro de série, la valeur est None et non une
        chaîne vide, sinon deux matériels entreraient en conflit
        d'unicité en base.
        """
        mapper = WinAuditMapper({"Résumé du Système": {}}, None)

        self.assertIsNone(mapper.map_equipement()["numero_serie"])

    def test_rapport_reprend_les_informations_techniques(self):
        rapport = self.mapper.map_rapport_audit()

        self.assertEqual(
            rapport["system_exploitation"],
            "Windows 10 Professionnel",
        )
        self.assertEqual(
            rapport["processeur"],
            "Intel(R) Core(TM) i5-9400",
        )
        self.assertEqual(rapport["memoire"], "8,00 Go")
        self.assertEqual(rapport["stockage"], "256,00 Go")
        self.assertEqual(rapport["bios"], "1.2.3")

    def test_rapport_conserve_les_donnees_brutes(self):
        """RG-W04 : les données brutes de l'audit sont conservées."""
        rapport = self.mapper.map_rapport_audit()

        self.assertEqual(rapport["donnees_brutes"], self.donnees)

    def test_la_date_d_audit_est_transmise_au_rapport(self):
        from datetime import datetime
        from django.utils import timezone

        date_audit = timezone.make_aware(
            datetime(2021, 3, 19, 7, 32, 5)
        )
        mapper = WinAuditMapper(self.donnees, date_audit)

        self.assertEqual(
            mapper.map_rapport_audit()["date_audit"],
            date_audit,
        )
