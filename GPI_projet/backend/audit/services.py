from pathlib import Path
from inventaire.models.equipement import Equipement
from audit.models import RapportAudit

from .parser import WinAuditParser
from .mapping import WinAuditMapper

class WinAuditService:
    """
    Synchronisation de l'inventaire à partir d'une collecte WinAudit.

    Sur un équipement existant, seuls les champs techniques collectés
    par WinAudit sont rafraîchis : l'état, la situation, la salle et la
    condition de stock restent pilotés par GPI (RG-E04, RG-E05, RG-E06).
    """

    # Champs que la collecte WinAudit a le droit de mettre à jour.
    CHAMPS_SYNCHRONISES = (
        "nom",
        "type",
        "numero_serie",
        "fabricant",
        "modele",
        "adresse_ip",
        "adresse_mac",
    )

    # Identifiants sans lesquels la synchronisation n'est pas possible :
    # une clé vide fusionnerait deux matériels distincts sous une seule
    # fiche d'inventaire.
    CHAMPS_IDENTIFIANTS = (
        "nom",
        "numero_inventaire",
    )

    def __init__(self, file_path: Path):
        self.file_path = file_path

    @staticmethod
    def _valider_identifiants(donnees: dict) -> None:
        """
        Vérifie que le rapport permet d'identifier un matériel.

        Un rapport incomplet est rejeté : mieux vaut une erreur explicite
        (fichier archivé dans le dossier des échecs) qu'un écrasement
        silencieux d'une fiche existante.
        """
        manquants = [
            champ
            for champ in WinAuditService.CHAMPS_IDENTIFIANTS
            if not donnees.get(champ)
        ]

        if manquants:
            raise ValueError(
                "Le rapport WinAudit ne fournit pas "
                f"l'identifiant du matériel : {', '.join(manquants)}."
            )

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

        #Contrôle des identifiants avant toute écriture en base
        self._valider_identifiants(donnees_equipement)

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

        if created:
            return equipement

        #L'équipement existe déjà : seuls les champs techniques issus de
        #la collecte sont synchronisés. L'état, la situation, la salle et
        #la condition de stock restent gérés par GPI.
        champs = [
            champ
            for champ in WinAuditService.CHAMPS_SYNCHRONISES
            if champ in donnees
        ]

        for champ in champs:
            setattr(equipement, champ, donnees[champ])

        if champs:
            equipement.save(update_fields=champs)

        return equipement
