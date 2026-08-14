from django.db import models
from .etage import Etage

class Salle (models.Model):
    etage = models.ForeignKey(
        Etage,
        on_delete = models.CASCADE,
        related_name="salles",
    )

    nom = models.CharField(
        max_length = 100,
    )

    description = models.TextField(
        blank = True,
    )

    def __str__(self):
        return f"{self.etage} - {self.nom}"