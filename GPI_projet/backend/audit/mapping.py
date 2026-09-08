from typing import Any
class WinAuditMapper:
    def __init__(self, data: dict[str, dict[str, str]], date_audit = None):
        self.data = data
        self.date_audit = date_audit
    def map_equipement(self) -> dict[str, Any]:
        system = self.data.get("Résumé du Système", {})
        return{
            "nom": self._get_value(system,"Computer Name",),
            "type": "ORDINATEUR",
            "numero_inventaire": self._get_value(
                system,"Asset Tag",
            ),
            "numero_serie": self._get_value(
                system, "Serial Number",
            ),
            "fabricant": self._get_value(
                system, "Manufacturer,"
            ),
            "modele": self._get_value(
                system, "Model",
            ),
            "adresse_ip": None,
            "adresse_mac": "",
            "salle":None,
            "actif": True,
        }

    def map_rapport_audit(self) -> dict[str, Any]:
        systeme = self.data.get("Résumé du Système", {})
        return {
            "date_audit": self.date_audit,
            "systeme_exploitation": self._get_value(
                systeme,
                "Operating System"
            ),
            "processeur": self._get_value(
                systeme,
                "Processor Description"
            ),
            "memoire": self._get_value(
                systeme,
                "Total Memory"
            ),

            "stockage": self._get_value(
                systeme,
                "Total Hard Drive"
            ),

            "bios": self._get_value(
                systeme,
                "BIOS Version"
            ),

            "donnees_brutes": self.data,

        }
    @staticmethod
    def _get_value(
        section: dict[str, str],
        key: str,
        default: str = "",
    ) -> str :
        return section.get(key, default).strip()