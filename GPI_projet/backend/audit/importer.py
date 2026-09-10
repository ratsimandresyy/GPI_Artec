from pathlib import Path
from .services import WinAuditService

class WinAuditImporter :
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)

    def importer(self):
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Le fichier WinAudit n'existe pas : {self.file_path}"
    )

        if not self.file_path.is_file():
            raise ValueError(
                f"Le chemin indiqué n'est pas un fichier : {self.file_path}"
            )

        service = WinAuditService(self.file_path)
        return service.importer()