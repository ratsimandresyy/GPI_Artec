from django.db import transaction
from django.utils import timezone

from ..models.equipement import Equipement
from ..models.ticket_panne import TicketPanne

class PanneService:

    #Etats que peut prendre un materiel a la resolution du ticket.
    #Diagramme d'activite : "Materiel repare ?" Oui -> EN_SERVICE,
    #Non -> HORS_SERVICE.
    ETATS_APRES_RESOLUTION = ("EN_SERVICE", "HORS_SERVICE")

    #Qualification possible d'un ticket.
    TYPES_VALIDES = ("MAINTENANCE", "RECLAMATION")
    PRIORITES_VALIDES = ("BASSE", "NORMALE", "HAUTE", "CRITIQUE")

    @staticmethod
    @transaction.atomic
    def declarer_panne(
        equipement: Equipement,
        titre: str,
        description: str,
        type: str = "MAINTENANCE",
        priorite: str = "NORMALE",
    ) -> TicketPanne:
        if not titre or not titre.strip():
            raise ValueError(
                "Le titre du ticket est obligatoire."
            )

        if not description or not description.strip():
            raise ValueError(
                "La description de la panne est obligatoire."
            )

        if equipement.etat == "EN_PANNE":
            raise ValueError(
                "Cet équipement est déjà en panne."
            )
        equipement.etat = "EN_PANNE"
        equipement.save(update_fields=["etat"])

        ticket = TicketPanne.objects.create(
            equipement = equipement,
            titre = titre,
            description = description,
            type = type,
            priorite = priorite,
        )

        return ticket

    @staticmethod
    @transaction.atomic
    def qualifier_ticket(
        ticket: TicketPanne,
        type: str | None = None,
        priorite: str | None = None,
    ) -> TicketPanne:
        """
        Qualifie un ticket : type et/ou priorite.

        L'administrateur peut requalifier un ticket apres sa creation
        (diagramme d'activite : "Qualifier le ticket : definir le type,
        definir la priorite").
        """
        if type is None and priorite is None:
            raise ValueError(
                "Aucune qualification fournie : "
                "renseignez le type et/ou la priorité."
            )

        champs = []

        if type is not None:
            if type not in PanneService.TYPES_VALIDES:
                raise ValueError(
                    f"Type de ticket invalide : {type}."
                )

            ticket.type = type
            champs.append("type")

        if priorite is not None:
            if priorite not in PanneService.PRIORITES_VALIDES:
                raise ValueError(
                    f"Priorité de ticket invalide : {priorite}."
                )

            ticket.priorite = priorite
            champs.append("priorite")

        ticket.save(update_fields=champs)

        return ticket

    @staticmethod
    @transaction.atomic
    def prendre_en_charge(ticket: TicketPanne) -> TicketPanne:
        if ticket.statut != "OUVERT":
            raise ValueError(
                "Seul un ticket ouvert peut être pris en charge."
            )

        ticket.statut = "EN_COURS"
        ticket.save(update_fields=["statut"])

        return ticket

    @staticmethod
    @transaction.atomic
    def resoudre_ticket(
        ticket: TicketPanne,
        commentaire_resolution: str,
        etat_final: str = "EN_SERVICE",
    ) -> TicketPanne:
        """
        Cloture un ticket.

        L'etat final du materiel depend du diagnostic : EN_SERVICE si le
        materiel est repare, HORS_SERVICE sinon (diagramme d'activite).
        """
        if ticket.statut != "EN_COURS":
            raise ValueError(
                "Seul un ticket en cours peut être résolu."
            )

        if etat_final not in PanneService.ETATS_APRES_RESOLUTION:
            raise ValueError(
                "L'état final du matériel doit être "
                "EN_SERVICE ou HORS_SERVICE."
            )

        ticket.statut = "RESOLU"
        ticket.date_resolution = timezone.now()
        ticket.commentaire_resolution = commentaire_resolution

        ticket.save(
            update_fields=[
                "statut",
                "date_resolution",
                "commentaire_resolution",
            ]
        )

        equipement = ticket.equipement
        equipement.etat = etat_final

        equipement.save(update_fields=["etat"])

        return ticket