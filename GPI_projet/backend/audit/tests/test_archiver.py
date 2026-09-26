"""
Tests de l'archivage des fichiers WinAudit traités.

Étape « Archiver le fichier traité » du diagramme de séquence.
"""

import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from audit.archiver import WinAuditArchiver


class WinAuditArchiverTest(SimpleTestCase):
    """L'archiver déplace les fichiers sans jamais les écraser."""

    NOM_FICHIER = "AD1_AD1$_20210319_0732.txt"

    def setUp(self):
        self.dossier_temporaire = tempfile.TemporaryDirectory()
        self.racine = Path(self.dossier_temporaire.name)
        self.archiver = WinAuditArchiver(self.racine)

    def tearDown(self):
        self.dossier_temporaire.cleanup()

    def _creer_fichier(self, nom=None):
        fichier = self.racine / (nom or self.NOM_FICHIER)
        fichier.write_text(
            "Audit de l'Ordinateur :: 19/03/2021 07:32:05",
            encoding="cp1252",
        )
        return fichier

    def test_les_dossiers_d_archive_sont_derives_de_la_racine(self):
        self.assertEqual(
            self.archiver.dossier_traites,
            self.racine / "traites",
        )
        self.assertEqual(
            self.archiver.dossier_echecs,
            self.racine / "echecs",
        )

    def test_archiver_deplace_le_fichier_dans_traites(self):
        fichier = self._creer_fichier()

        destination = self.archiver.archiver(fichier)

        self.assertFalse(fichier.exists())
        self.assertTrue(destination.exists())
        self.assertEqual(destination.parent, self.archiver.dossier_traites)
        self.assertEqual(destination.name, self.NOM_FICHIER)

    def test_archiver_cree_les_dossiers_au_besoin(self):
        fichier = self._creer_fichier()

        self.archiver.archiver(fichier)

        self.assertTrue(self.archiver.dossier_traites.is_dir())

    def test_rejeter_deplace_le_fichier_dans_echecs(self):
        fichier = self._creer_fichier()

        destination = self.archiver.rejeter(fichier)

        self.assertFalse(fichier.exists())
        self.assertEqual(destination.parent, self.archiver.dossier_echecs)

    def test_un_fichier_deja_archive_n_est_jamais_ecrase(self):
        premier = self._creer_fichier()
        destination_premier = self.archiver.archiver(premier)

        second = self._creer_fichier()
        destination_second = self.archiver.archiver(second)

        self.assertNotEqual(destination_premier, destination_second)
        self.assertEqual(
            destination_second.name,
            "AD1_AD1$_20210319_0732_1.txt",
        )
        self.assertEqual(
            len(list(self.archiver.dossier_traites.iterdir())),
            2,
        )

    def test_l_archivage_conserve_le_contenu_du_fichier(self):
        fichier = self._creer_fichier()
        contenu = fichier.read_bytes()

        destination = self.archiver.archiver(fichier)

        self.assertEqual(destination.read_bytes(), contenu)

    def test_un_fichier_absent_leve_une_erreur(self):
        with self.assertRaises(FileNotFoundError):
            self.archiver.archiver(self.racine / "inexistant.txt")
