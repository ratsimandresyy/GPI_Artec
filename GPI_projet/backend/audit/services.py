from pathlib import Path
from inventaire.models.equipement import Equipement
from audit.models import RapportAudit

from .parser import WinAuditParser
from .mapping import WinAuditMapper

class WinAuditService:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def importer(self) -> RapportAudit:
        #lecture du fichier WinAudit
        parser = WinAuditParser(self.file_path)

        data = parser.parse()
        date_audit = parser.parse_date_audit()

        #Transformez les données
        mapper = WinAuditMapper(
            data, date_audit,
        )

        donnees_equipement = mapper.map_equipement()
        donnees_rapport = mapper.map_rapport_audit()

        #Rechercher ou création de l'équipement
        equipement = self._get_or_create_equipement(
            donnees_equipement
        )

        #Association du rapport à l'équipement
        donnees_rapport["equipement"] = equipement

        #Création du rapport d'audit
        rapport = RapportAudit.objects.create(
            **donnees_rapport
        )

        return rapport

    @staticmethod
    def _get_or_create_equipement(
        donnees: dict,
    ) -> Equipement :

        equipement, created = Equipement.objects.get_or_create(
            numero_inventaire = donnees["numero_inventaire"],
            defaults = donnees,
        )

        if not created :
            for champ, valeur in donnees.items():
                if champ != "numero_inventaire":
                    setattr(equipement, champ, valeur)

            equipement.save()
        return equipement
