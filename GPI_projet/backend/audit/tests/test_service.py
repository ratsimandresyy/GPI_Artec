"""
Tests du service d'importation des rapports WinAudit.

Couvre l'étape « Synchroniser l'inventaire » du diagramme de séquence :
si le matériel existe, ses informations techniques sont mises à jour ;
sinon un nouvel actif est créé. Le rapport d'audit est rattaché à
l'équipement dans les deux cas, afin de conserver l'historique.
"""

from datetime import datetime
from pathlib import Path

from django.test import TestCase
from django.utils import timezone

from audit.importer import WinAuditImporter
from audit.models import RapportAudit
from audit.services import WinAuditService
from inventaire.models.equipement import Equipement


FIXTURE = Path(__file__).parent / "fixtures" / "winaudit_exemple.txt"
FIXTURE_SANS_SERIE = (
    Path(__file__).parent / "fixtures" / "winaudit_sans_numero_serie.txt"
)
FIXTURE_SANS_IDENTIFIANT = (
    Path(__file__).parent / "fixtures" / "winaudit_sans_identifiant.txt"
)


class WinAuditImporterTest(TestCase):
    """La façade d'importation valide le fichier avant de déléguer."""

    def test_un_fichier_absent_leve_une_erreur(self):
        importer = WinAuditImporter(
            FIXTURE.parent / "fichier_inexistant.txt"
        )

        with self.assertRaises(FileNotFoundError):
            importer.importer()

    def test_un_dossier_leve_une_erreur(self):
        importer = WinAuditImporter(FIXTURE.parent)

        with self.assertRaises(ValueError):
            importer.importer()


class WinAuditServiceTest(TestCase):
    """Synchronisation de l'inventaire à partir d'une collecte (RG08)."""

    def setUp(self):
        self.service = WinAuditService(FIXTURE)

    def test_un_nouvel_equipement_est_cree_depuis_la_collecte(self):
        rapport = self.service.importer()

        equipement = Equipement.objects.get()

        self.assertEqual(equipement.nom, "AD1")
        self.assertEqual(equipement.numero_inventaire, "INV-2021-001")
        self.assertEqual(equipement.numero_serie, "SERIE-0001")
        self.assertEqual(equipement.fabricant, "Dell Inc.")
        self.assertEqual(equipement.modele, "OptiPlex 3070")
        self.assertEqual(equipement.type, "ORDINATEUR")
        self.assertEqual(rapport.equipement, equipement)

    def test_un_nouvel_equipement_est_affecte_et_sans_salle(self):
        self.service.importer()

        equipement = Equipement.objects.get()

        self.assertEqual(equipement.situation, "AFFECTE")
        self.assertEqual(equipement.etat, "EN_SERVICE")
        self.assertIsNone(equipement.salle)
        self.assertIsNone(equipement.condition_stock)

    def test_le_rapport_d_audit_reprend_les_informations_techniques(self):
        rapport = self.service.importer()

        self.assertEqual(
            rapport.system_exploitation,
            "Windows 10 Professionnel",
        )
        self.assertEqual(
            rapport.processeur,
            "Intel(R) Core(TM) i5-9400 CPU @ 2.90GHz",
        )
        self.assertEqual(rapport.memoire, "8,00 Go")
        self.assertEqual(rapport.stockage, "256,00 Go")
        self.assertEqual(rapport.bios, "1.2.3")

    def test_le_rapport_est_date_et_conserve_les_donnees_brutes(self):
        rapport = self.service.importer()

        self.assertEqual(
            rapport.date_audit,
            timezone.make_aware(datetime(2021, 3, 19, 7, 32, 5)),
        )
        self.assertEqual(
            rapport.donnees_brutes["Résumé du Système"]["Computer Name"],
            "AD1",
        )

    def test_un_second_import_met_a_jour_sans_creer_de_doublon(self):
        """RG-W02 : plusieurs collectes, un seul équipement."""
        self.service.importer()
        self.service.importer()

        self.assertEqual(Equipement.objects.count(), 1)
        self.assertEqual(RapportAudit.objects.count(), 2)

    def test_l_import_rafraichit_les_informations_techniques(self):
        self.service.importer()

        equipement = Equipement.objects.get()
        equipement.fabricant = "Ancien fabricant"
        equipement.modele = "Ancien modele"
        equipement.save(update_fields=["fabricant", "modele"])

        self.service.importer()
        equipement.refresh_from_db()

        self.assertEqual(equipement.fabricant, "Dell Inc.")
        self.assertEqual(equipement.modele, "OptiPlex 3070")

    def test_l_import_ne_remet_pas_en_service_un_materiel_en_panne(self):
        """
        RG-E04 : l'état du matériel est piloté par GPI (tickets,
        maintenance) et non par la collecte WinAudit.
        """
        self.service.importer()

        equipement = Equipement.objects.get()
        equipement.etat = "EN_PANNE"
        equipement.save(update_fields=["etat"])

        self.service.importer()
        equipement.refresh_from_db()

        self.assertEqual(equipement.etat, "EN_PANNE")

    def test_l_import_ne_modifie_pas_la_situation_du_materiel(self):
        """
        RG-E06 / RG-E07 : un matériel en stock le reste après une
        collecte, avec sa condition de stock.
        """
        self.service.importer()

        equipement = Equipement.objects.get()
        equipement.situation = "EN_STOCK"
        equipement.condition_stock = "NEUF"
        equipement.save(update_fields=["situation", "condition_stock"])

        self.service.importer()
        equipement.refresh_from_db()

        self.assertEqual(equipement.situation, "EN_STOCK")
        self.assertEqual(equipement.condition_stock, "NEUF")

    def test_un_materiel_sans_numero_de_serie_est_accepte(self):
        """RG-E03 : le numéro de série est facultatif."""
        service = WinAuditService(FIXTURE_SANS_SERIE)

        service.importer()

        equipement = Equipement.objects.get()

        self.assertEqual(equipement.numero_inventaire, "INV-2021-002")
        self.assertIsNone(equipement.numero_serie)

    def test_deux_numeros_de_serie_absents_coexistent(self):
        """
        RG-E03 : plusieurs matériels sans numéro de série peuvent
        coexister (deux NULL ne violent pas la contrainte d'unicité,
        contrairement à deux chaînes vides).
        """
        WinAuditService(FIXTURE_SANS_SERIE).importer()

        Equipement.objects.create(
            nom="AD3",
            type="ORDINATEUR",
            numero_inventaire="INV-2021-003",
            numero_serie=None,
        )

        self.assertEqual(
            Equipement.objects.filter(numero_serie__isnull=True).count(),
            2,
        )

    def test_un_rapport_sans_identifiant_est_rejete(self):
        """
        Sans nom ni numéro d'inventaire, la synchronisation est refusée :
        une clé vide fusionnerait deux matériels distincts sous une même
        fiche d'inventaire.
        """
        service = WinAuditService(FIXTURE_SANS_IDENTIFIANT)

        with self.assertRaises(ValueError):
            service.importer()

        self.assertEqual(Equipement.objects.count(), 0)
        self.assertEqual(RapportAudit.objects.count(), 0)

