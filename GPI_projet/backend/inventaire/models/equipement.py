from django.db import models
from .salle import Salle

class TypeEquipement(models.TextChoices):
    """
    Types d'équipement pris en charge
    """
    ORDINATEUR = "ORDINATEUR", "Ordinateur"

class Equipement(models.Model):
    nom = models.CharField(
        max_length = 100,
        unique = True,
    )

    type = models.CharField(
        max_length = 20,
        choices = TypeEquipement.choices,
    )

    fabricant = models.CharField(
        max_length = 100,
        blank = True,
    )

    modele = models.CharField(
        max_length = 100,
        blank = True,
    )

    numero_inventaire = models.CharField(
        max_length = 100,
        unique = True,
    )

    numero_serie = models.CharField(
        max_length = 100,
        unique = True,
        blank = True,
    )

    adresse_ip = models.GenericIPAddressField(
        null = True,
        blank = True,
    )

    adresse_mac = models.CharField(
        max_length = 17,
        blank = True,
    )

    salle = models.ForeignKey(
        Salle,
        on_delete = models.SET_NULL,
        null = True,
        blank = True,
        related_name = "equipements",
    )

    actif = models.BooleanField(
        default = True,
    )

    def __str__(self):
        return self.nom