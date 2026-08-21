from django.db import models
from .etage import Etage

class Plan(models.Model):
    etage = models.OneToOneField(
        Etage,
        on_delete = models.CASCADE,
        related_name = "plan",
    )

    image = models.ImageField(
        upload_to = "plans/",
    )

    largeur = models.PositiveBigIntegerField(
        null = True,
        blank = True,
    )

    hauteur = models.PositiveBigIntegerField(
        null = True,
        blank = True,
    )

    def __str__(self):
        return f"Plan - {self.etage.nom}"