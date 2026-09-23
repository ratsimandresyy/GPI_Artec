from django.db import transaction
from django.utils import timezone

from ..models.equipement import Equipement
from ..models.ticket_panne import TicketPanne

class PanneService:
    @staticmethod
    @transaction.atomic
    def declarer_panne(
        equipement: Equipement,
        description: str,
    ) -> TicketPanne:
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
            description = description
        )

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
    ) -> TicketPanne:
        if ticket.statut != "EN_COURS":
            raise ValueError(
                "Seul un ticket en cours peut être résolu."
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
        equipement.etat = "EN_SERVICE"

        equipement.save(update_fields=["etat"])

        return ticket