from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from audit.importer import WinAuditImporter

class Command(BaseCommand):

    help = "Importe un fichier WinAudit dans la base de données."

    def add_arguments(self, parser):
        parser.add_argument("fichier", type=str, help="Chemin vers le fichier WinAudit à importer.")

    def handle(self, *args, **options):
        fichier = Path(options["fichier"])
        if not fichier.exists():
            raise CommandError(
                f"Le fichier n'existe pas : {fichier}"
            )
        try:
            importer = WinAuditImporter(fichier)
            rapport = importer.importer()

        except Exception as erreur:
            raise CommandError(
                f"Erreur pendant l'importation : {erreur}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Importation terminée avec succès."
            )
        )

        self.stdout.write(
            f"Rapport d'audit crée : ID {rapport.id}"
        )