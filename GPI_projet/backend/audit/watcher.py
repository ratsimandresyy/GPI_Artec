import time 
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from .importer import WinAuditImporter

class WinAuditWatcher(FileSystemEventHandler):
    def __init__(self, dossier: str | Path):
        super().__init__()

        self.dossier = Path(dossier)

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
        except Exception as erreur:
            print(
                "Erreur lors de l'importation de "
                f"{fichier} : {erreur}"
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
def demarrer_watcher(dossier: str | Path):
    dossier = Path(dossier)

        #Création du dossier s'il n'éxiste pas
    dossier.mkdir(
        parents=True,
        exist_ok=True,
    )

    watcher = WinAuditWatcher(dossier)

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

    try :
        while True:
            #Le watcher reste actif et attend les nouveaux fichiers
            time.sleep(2)
    except KeyboardInterrupt:
           print("Arrêt du watcher...")

    observer.stop()

    observer.join()