"""
Tests d'isolement du MEDIA_ROOT (Etape 6).

Les tests ne doivent jamais ecrire dans le dossier media reel du
projet. Ces tests verifient que le MEDIA_ROOT actif est temporaire et
que les uploads qu'ils declenchent restent confines.
"""

import os
import tempfile
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.plan import Plan


MEDIA_REEL = Path(settings.BASE_DIR) / "media"


def _image_contenu(nom=None):
    """Minimal PNG valide (1x1) pour l'ImageField."""
    contenu = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
        b"\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00"
        b"\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    # Un nom unique par execution : la verification d'absence dans le
    # MEDIA_ROOT reel ne peut pas être satisfaite par un fichier
    # laisse par une ancienne execution.
    if nom is None:
        nom = f"plan_{uuid.uuid4().hex}.png"

    return SimpleUploadedFile(nom, contenu, content_type="image/png")


class MediaRootIsoleTest(TestCase):

    def test_le_media_root_actif_n_est_pas_celui_du_projet(self):
        self.assertNotEqual(
            Path(settings.MEDIA_ROOT),
            MEDIA_REEL,
            "Les tests ecrivent dans le MEDIA_ROOT reel de l'application.",
        )

    def test_le_media_root_actif_est_temporaire(self):
        racine = Path(settings.MEDIA_ROOT)

        # Un TemporaryDirectory vit sous le dossier temporaire du systeme.
        self.assertNotIn(
            "gestion_de_PI",
            str(racine),
            "Le MEDIA_ROOT des tests doit etre hors du projet.",
        )

    def test_un_media_root_normal_n_est_pas_modifie(self):
        """
        settings.py conserve le MEDIA_ROOT de l'application ; c'est le
        runner qui le remplace le temps des tests.
        """
        contenu = (MEDIA_REEL.parent / "config" / "settings.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('MEDIA_ROOT = BASE_DIR / "media"', contenu)


class UploadIsoleTest(TestCase):
    """Les uploads restent possibles, mais dans le repertoire temporaire."""

    def setUp(self):
        self.batiment = Batiment.objects.create(nom="Bâtiment Média")

        self.etage = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="RDC",
        )

    def test_un_plan_peut_toujours_etre_televerse(self):
        plan = Plan.objects.create(
            etage=self.etage,
            image=_image_contenu(),
            largeur=1000,
            hauteur=800,
        )

        self.assertTrue(plan.image.name.startswith("plans/"))
        self.assertTrue(plan.pk)
    def test_le_fichier_est_ecrit_dans_le_media_root_temporaire(self):
        plan = Plan.objects.create(
            etage=self.etage,
            image=_image_contenu(),
        )

        chemin = Path(settings.MEDIA_ROOT) / plan.image.name

        self.assertTrue(
            chemin.exists(),
            "Le fichier televerse doit exister dans le MEDIA_ROOT actif.",
        )

        # Et il ne doit surtout pas apparaitre dans le media du projet.
        self.assertFalse(
            (MEDIA_REEL / plan.image.name).exists(),
            "Un fichier de test a ete ecrit dans le MEDIA_ROOT reel.",
        )

    def test_le_contenu_televerse_est_integre(self):
        plan = Plan.objects.create(
            etage=self.etage,
            image=_image_contenu(),
        )

        try:
            plan.image.seek(0)
            contenu = plan.image.read()
        finally:
            # Sous Windows, un fichier ouvert ne peut pas etre supprime :
            # le handle doit etre libere avant le nettoyage du dossier.
            plan.image.close()

        self.assertTrue(contenu.startswith(b"\x89PNG"))
        self.assertGreater(len(contenu), 0)
