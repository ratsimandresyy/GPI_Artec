from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from audit.watcher import demarrer_watcher

class Command(BaseCommand):
    help = "Surveille un dossier pour importer automatiquement les fichier WinAudit. "

    def add_arguments(self, parser):
        parser.add_argument(
            "dossier",
            type=str,
            help="Dossier contenant les fichiers WinAudit.",
        )
    def handle(self, *args, **options):
        dossier = Path(options["dossier"])

        try :
            self.stdout.write(
                self.style.SUCCESS(
                    f"Surveillance de : {dossier}"
                )
            )

            demarrer_watcher(dossier)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING(
                    "Watcher arrêté."
                )
            )

        except Exception as erreur:
            raise CommandError(
                f"Erreur du watcher : {erreur}"
            )