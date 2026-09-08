from pathlib import Path
from datetime import datetime

class WinAuditParser:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def parse(self) -> dict[str, dict[str, str]]:
        data = {}
        current_section = None
        with self.file_path.open(
            "r",
            encoding="cp1252",
            errors="replace",
        ) as file:
            for line in file:
                section = self._parse_section(line)

                if section:
                    current_section = section
                    data[current_section] = {}
                    continue
                key, value = self._parse_line(line)

                if key and current_section:
                    data[current_section][key] = value
        return data

    def parse_date_audit(self) -> datetime | None:
        with self.file_path.open(
            "r",
            encoding="cp1252",
            errors="replace",
        ) as file:
            for line in file:
                line = line.strip()

                if line.startswith("Audit de l'Ordinateur"):
                    try:
                        date_str = line.split("::", 1)[1].strip()
                        return datetime.strptime(
                            date_str,
                            "%d/%m/%Y %H:%M:%S",
                        )
                    except (IndexError, ValueError):
                        return None

    @staticmethod
    def _parse_section(line: str,) -> str | None:
        line = line.strip()

        # Ignore les ligne vide
        if not line:
            return None

        # Une ligne commencant par | appartient à un tableau de données.
        if line.startswith("|"):
            return None

        # Ignore les séparateurs constitués principalement de tirets.
        if line.replace("-", "").strip() == "":
            return None

        # Ignore le pied de page WinAudit.
        sections = {
            "Résumé du Système",
            "Système d'Exploitation",
            "Périphériques",
        }

        if line in sections:
            return line
            
        return None

    @staticmethod
    def _parse_line(line: str) -> tuple[str | None, str | None]:
        line = line.strip()

        if not line.startswith("|"):
            return None, None

        parts = line.strip("|").split("|")

        if len(parts) < 2:
            return None, None

        key = parts[0].strip()
        value = parts[1].strip()

        if not key or not value:
            return None, None

        # En-têtes des tableaux WinAudit
        if (key, value) in {
            ("Item", "Value"),
            ("Name", "Description"),
        }:
            return None, None

        return key, value