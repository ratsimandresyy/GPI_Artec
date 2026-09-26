"""
Archivage des fichiers WinAudit traités.

Étape « Archiver le fichier traité » du diagramme de séquence :
le fichier analysé est déplacé vers un dossier d'archive afin de
conserver la trace des collectes et de ne pas être ré-importé.

Ce module ne dépend pas de Django : il est injecté dans le watcher
(principe d'inversion des dépendances) et reste testable isolément.
"""

import shutil
from pathlib import Path


class WinAuditArchiver:
    """
    Déplace les fichiers WinAudit vers un dossier d'archive.

    Responsabilité unique : déplacer un fichier.
    L'archiver ne lit ni n'interprète jamais le contenu du fichier.
    """

    SOUS_DOSSIER_TRAITES = "traites"
    SOUS_DOSSIER_ECHECS = "echecs"

    def __init__(self, racine: str | Path):
        self.racine = Path(racine)

    @property
    def dossier_traites(self) -> Path:
        """Dossier des fichiers importés avec succès."""
        return self.racine / self.SOUS_DOSSIER_TRAITES

    @property
    def dossier_echecs(self) -> Path:
        """Dossier des fichiers dont l'importation a échoué."""
        return self.racine / self.SOUS_DOSSIER_ECHECS

    def archiver(self, fichier: str | Path) -> Path:
        """
        Archive un fichier importé avec succès.

        Retourne le chemin de la copie archivée.
        """
        return self._deplacer(
            fichier=Path(fichier),
            dossier=self.dossier_traites,
        )

    def rejeter(self, fichier: str | Path) -> Path:
        """
        Archive un fichier dont l'importation a échoué.

        Le fichier est conservé pour permettre une reprise manuelle.
        Retourne le chemin de la copie archivée.
        """
        return self._deplacer(
            fichier=Path(fichier),
            dossier=self.dossier_echecs,
        )

    @staticmethod
    def _destination_libre(dossier: Path, nom: str) -> Path:
        """
        Retourne un chemin libre dans le dossier d'archive.

        Un fichier déjà archivé ne doit jamais être écrasé : un suffixe
        numérique est ajouté jusqu'à trouver un nom disponible.
        """
        destination = dossier / nom
        compteur = 1
        fichier = Path(nom)

        while destination.exists():
            destination = dossier / (
                f"{fichier.stem}_{compteur}{fichier.suffix}"
            )
            compteur += 1

        return destination

    def _deplacer(self, fichier: Path, dossier: Path) -> Path:
        if not fichier.exists():
            raise FileNotFoundError(
                f"Le fichier à archiver n'existe pas : {fichier}"
            )

        dossier.mkdir(
            parents=True,
            exist_ok=True,
        )

        destination = self._destination_libre(
            dossier=dossier,
            nom=fichier.name,
        )

        shutil.move(
            str(fichier),
            str(destination),
        )

        return destination
