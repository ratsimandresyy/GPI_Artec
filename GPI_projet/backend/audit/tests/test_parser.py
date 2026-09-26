"""
Tests du parser des rapports WinAudit.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from django.test import SimpleTestCase
from django.utils import timezone

from audit.parser import WinAuditParser


FIXTURE = Path(__file__).parent / "fixtures" / "winaudit_exemple.txt"


class WinAuditParserTest(SimpleTestCase):
    """Le parser lit un export WinAudit encodé en cp1252."""

    def setUp(self):
        self.parser = WinAuditParser(FIXTURE)

    def test_la_fixture_reproduit_l_encodage_winaudit(self):
        """
        Un export WinAudit est encodé en cp1252 (Windows-1252).

        Si la fixture était réécrite en UTF-8, les sections accentuées
        ne seraient plus détectées : ce test le signalerait.
        """
        contenu = FIXTURE.read_text(encoding="cp1252")

        self.assertIn("Audit de l'Ordinateur", contenu)
        self.assertIn("Résumé du Système", contenu)
        self.assertIn("Périphériques", contenu)

    def test_les_sections_connues_sont_detectees(self):
        donnees = self.parser.parse()

        self.assertEqual(
            sorted(donnees),
            ["Périphériques", "Résumé du Système"],
        )

    def test_les_valeurs_du_resume_du_systeme_sont_lues(self):
        systeme = self.parser.parse()["Résumé du Système"]

        self.assertEqual(systeme["Computer Name"], "AD1")
        self.assertEqual(systeme["Asset Tag"], "INV-2021-001")
        self.assertEqual(systeme["Serial Number"], "SERIE-0001")
        self.assertEqual(systeme["Manufacturer"], "Dell Inc.")

    def test_les_entetes_de_tableau_sont_ignores(self):
        donnees = self.parser.parse()

        self.assertNotIn("Item", donnees["Résumé du Système"])
        self.assertNotIn("Name", donnees["Périphériques"])

    def test_les_separateurs_ne_deviennent_pas_des_sections(self):
        donnees = self.parser.parse()

        for section in donnees:
            self.assertNotIn("---", section)

    def test_la_date_d_audit_est_convertie(self):
        self.assertEqual(
            self.parser.parse_date_audit(),
            timezone.make_aware(datetime(2021, 3, 19, 7, 32, 5)),
        )

    def test_un_rapport_sans_date_ne_leve_pas_d_erreur(self):
        with tempfile.TemporaryDirectory() as dossier:
            fichier = Path(dossier) / "sans_date.txt"
            fichier.write_text(
                "Résumé du Système\n",
                encoding="cp1252",
            )

            parser = WinAuditParser(fichier)

            self.assertIsNone(parser.parse_date_audit())

    def test_une_ligne_de_donnees_est_decoupee_en_cle_valeur(self):
        cle, valeur = WinAuditParser._parse_line(
            "| Computer Name | AD1 |"
        )

        self.assertEqual(cle, "Computer Name")
        self.assertEqual(valeur, "AD1")

    def test_une_ligne_sans_valeur_est_ignoree(self):
        self.assertEqual(
            WinAuditParser._parse_line("   "),
            (None, None),
        )

