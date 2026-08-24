from pathlib import Path

class WinAuditParser:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def parse(self) -> dict[str, dict[str, str]]:
        data = {}
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

    @staticmethod
    def _parse_section(line: str,) -> str | None:
        line = line.strip()

        if not line:
            return None

        if line.startswitch("|"):
            return None
        return line

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

        return key, value