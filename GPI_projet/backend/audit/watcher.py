import time 
from pathlib import Path
from django.conf import settings
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .archiver import WinAuditArchiver
from .importer import WinAuditImporter

class WinAuditWatcher(FileSystemEventHandler):
    def __init__(self, dossier: str | Path, archiver: WinAuditArchiver):
        super().__init__()

        self.dossier = Path(dossier)

        #L'archivage est injecté : le watcher ne décide pas où archiver.
        self.archiver = archiver

    def on_created(self, event):

        #ignorer les dossiers
        if event.is_directory:
            return
        fichier = Path(event.src_path)

        # On ne traite qu les fichiers TXT
        if fichier.suffix.lower() != ".txt":
            return

        print(f"Nouveau fichier WinAudit détecté : {fichier}")

        try :
            #Attendre aue le fichier soit completement dispo
            self._attendre_fichier(fichier)

            #Lancer l'importation
            importer = WinAuditImporter(fichier)

            rapport = importer.importer()

            print(
                "Importation reussi : "
                f"RapportAudit ID {rapport.id}"
            )

            #Archiver le fichier traité
            destination = self.archiver.archiver(fichier)

            print(
                f"Fichier archivé : {destination}"
            )

        except Exception as erreur:
            print(
                "Erreur lors de l'importation de "
                f"{fichier} : {erreur}"
            )

            self._archiver_echec(fichier)

    def _archiver_echec(self, fichier: Path):
        #Un fichier rejeté est conservé pour permettre une reprise manuelle.
        try :
            destination = self.archiver.rejeter(fichier)

            print(
                f"Fichier rejeté archivé : {destination}"
            )

        except Exception as erreur:
            #L'archivage ne doit jamais interrompre la surveillance.
            print(
                f"Archivage impossible pour {fichier} : {erreur}"
            )

    def _attendre_fichier(self, fichier: Path, tentatives = 10, delai: int = 2,):
        for tentative in range(tentatives):
            try:
                # Ouvrir le fichier en lecture permet de verifier qu'il n'est plus verouiller par un autre processus.
                with open(fichier, "r", encoding="cp1252",):
                    pass
                print(
                    f"Fichier disponnible : {fichier}"
                )
                return
            except PermissionError:
                print(
                    "Fichier encore utilise. "
                    "Nouvelle tentative. "
                    f"{tentative + 1}/{tentatives}..."
                )
                time.sleep(delai)
        raise PermissionError(
            "Le fichier reste inaccessible apres"
            f"{tentatives} tentatives : {fichier}"
        )
def demarrer_watcher(dossier: str | Path, racine_archives: str | Path | None = None):
    dossier = Path(dossier)

        #Création du dossier s'il n'éxiste pas
    dossier.mkdir(
        parents=True,
        exist_ok=True,
    )

    #Par défaut, les fichiers traités sont archivés dans media/audits.
    if racine_archives is None:
        racine_archives = Path(settings.MEDIA_ROOT) / "audits"

    archiver = WinAuditArchiver(racine_archives)

    watcher = WinAuditWatcher(dossier, archiver)

    observer = Observer()

    observer.schedule(
        watcher,
        str(dossier),
        recursive=False,
    )

    observer.start()

    print(
        f"Surveillance du dossier : {dossier}"
    )

    print(
        f"Archivage des fichiers traités : {archiver.dossier_traites}"
    )

    try :
        while True:
            #Le watcher reste actif et attend les nouveaux fichiers
            time.sleep(2)
    except KeyboardInterrupt:
           print("Arrêt du watcher...")

    observer.stop()

    observer.join()
