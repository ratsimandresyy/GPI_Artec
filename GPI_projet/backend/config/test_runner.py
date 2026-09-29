"""
Runner de tests du GPI.

Les tests creent des images (plans) via le champ ImageField du modele
Plan. Sans precaution, ces fichiers atterrissent dans le vrai
MEDIA_ROOT du projet et s'y accumulent.

Ce runner redirige MEDIA_ROOT vers un repertoire temporaire pendant
la seule duree de la campagne de tests, puis le supprime. Le
MEDIA_ROOT de l'application n'est donc jamais modifie.
"""

import tempfile

from django.test.runner import DiscoverRunner
from django.test.utils import override_settings


class MediaIsoleTestRunner(DiscoverRunner):
    """
    Execute les tests avec un MEDIA_ROOT temporaire.

    L'override passe par override_settings : Django invalide alors
    le cache des storages, ce qui garantit que les uploads ettrits
    pendant les tests partent bien dans le repertoire temporaire.
    """

    def run_tests(self, test_labels, **kwargs):
        # ignore_cleanup_errors : sous Windows, un fichier encore ouvert
        # par un FileField ne peut pas etre supprime. Le dossier
        # temporaire est de toute facon hors du projet et vide de tout
        # fichier utilisateur, un reliquat est sans consequence.
        temporaire = tempfile.TemporaryDirectory(
            prefix="gpi-tests-media-",
            ignore_cleanup_errors=True,
        )

        with temporaire as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                return super().run_tests(test_labels, **kwargs)
