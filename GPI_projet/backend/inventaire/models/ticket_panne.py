from django.db import models
from .equipement import Equipement
from django.core.exceptions import ValidationError

class StatutTicket(models.TextChoices):
    OUVERT = "OUVERT", "Ouvert"
    EN_COURS = "EN_COURS", "En cours"
    RESOLU = "RESOLU", "Résolu"
    ANNULE = "ANNULE", "Annulé"

class TypeTicket(models.TextChoices):
    MAINTENANCE = "MAINTENANCE", "Maintenance"
    RECLAMATION = "RECLAMATION", "Réclamation"

class PrioriteTicket(models.TextChoices):
    BASSE = "BASSE", "Basse"
    NORMALE = "NORMALE", "Normale"
    HAUTE = "HAUTE", "Haute"
    CRITIQUE = "CRITIQUE", "Critique"

class TicketPanne(models.Model):

    equipement = models.ForeignKey(
        Equipement,
        on_delete=models.CASCADE,
        related_name="tickets_panne",
    )

    titre = models.CharField(
        max_length=200,
        default="",
    )

    type = models.CharField(
        max_length=20,
        choices=TypeTicket.choices,
        default=TypeTicket.MAINTENANCE,
    )

    priorite = models.CharField(
        max_length=20,
        choices=PrioriteTicket.choices,
        default=PrioriteTicket.NORMALE,
    )

    date_signalement = models.DateTimeField(
        auto_now_add=True,
    )

    description = models.TextField()

    statut = models.CharField(
        max_length=20,
        choices=StatutTicket.choices,
        default=StatutTicket.OUVERT,
    )

    date_resolution = models.DateTimeField(
        null=True,
        blank=True,
    )

    commentaire_resolution = models.TextField(
        blank=True,
    )

    def clean(self):
        if not self.titre or not self.titre.strip():
            raise ValidationError({
                "titre": "Le titre du ticket est obligatoire."
            })

        if self.statut == StatutTicket.RESOLU and not self.date_resolution:
                raise ValidationError({
                    "date_resolution": (
                    "Un ticket résolu doit avoir une date de résolution."
                )
            })

        if self.statut == StatutTicket.RESOLU and not self.commentaire_resolution.strip():
            raise ValidationError({
                "commentaire_resolution": (
                    "Un commentaire de résolution est obligatoire."
                )
            })

        if self.statut != StatutTicket.RESOLU and self.date_resolution:
            raise ValidationError({
                "date_resolution": (
                    "La date de résolution ne peut être renseignée "
                    "que pour un ticket résolu."
                )
            })

    def __str__(self):
        return (
            f"Panne - {self.equipement.nom}"
            f"({self.get_statut_display()})"
        )