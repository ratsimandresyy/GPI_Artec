from django.db import models
from .equipement import Equipement
from .plan import Plan

class Position(models.Model):
    equipement = models.OneToOneField(
        Equipement,
        on_delete = models.CASCADE,
        related_name = "position",
    )

    plan = models.ForeignKey(
        Plan,
        on_delete = models.CASCADE,
        related_name = "positions",
    )

    x = models.FloatField()
    y = models.FloatField()

    def __str__(self):
        return f"{self.equipement.nom} - ({self.x}, {self.y})"