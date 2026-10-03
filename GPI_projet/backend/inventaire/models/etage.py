from django.db import models
from .batiment import Batiment

class Etage(models.Model):
    batiment = models.ForeignKey(
        Batiment,
        on_delete = models.CASCADE,
        related_name = "etages",
    )

    numero = models.IntegerField()

    nom = models.CharField(
        max_length = 100,
        blank = True,
    )

    class Meta:
        unique_together = [
            ("batiment", "numero"),
            ("batiment", "nom"),
        ]

    def __str__(self):
        return f"{self.batiment.nom} - Etage {self.numero}"