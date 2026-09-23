from django.db import models
from .salle import Salle

class TypeEquipement(models.TextChoices):
    """
    Types d'équipement pris en charge
    """
    ORDINATEUR = "ORDINATEUR", "Ordinateur"

class EtatEquipement(models.TextChoices):
    EN_SERVICE = "EN_SERVICE", "En service"
    EN_PANNE = "EN_PANNE", "En panne"
    EN_MAINTENANCE = "EN_MAINTENANCE", "En maintenance"
    HORS_SERVICE = "HORS_SERVICE", "Hors service"

class SituationEquipement(models.TextChoices):
    AFFECTE = "AFFECTE", "Affecte"
    EN_STOCK = "EN_STOCK", "Stock"

class ConditionStock(models.TextChoices):
    NEUF = "NEUF", "Neuf"
    OCCASION = "OCCASION", "Occasion"
    RECONDITIONNE = "RECONDITIONNE", "Reconditionne"
    

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

    etat = models.CharField(
        max_length=20,
        choices=EtatEquipement.choices,
        default=EtatEquipement.EN_SERVICE,
    )

    situation = models.CharField(
        max_length=20,
        choices=SituationEquipement.choices,
        default=SituationEquipement.AFFECTE,
    )

    condition_stock = models.CharField(
        max_length=20,
        choices=ConditionStock.choices,
        null=True,
        blank=True
    )

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.situation == SituationEquipement.EN_STOCK:
            if not self.condition_stock:
                raise ValidationError({
                    "condition_stock": "La condition du matériel doit être renseignée lorsqu'il est en stock."
                })

            if self.salle:
                raise ValidationError({
                    "salle": (
                        "Un matériel en stock ne peut pas être affecté "
                        "à une salle."
                    )
            })

        elif self.situation == SituationEquipement.AFFECTE:
            self.condition_stock = None

    def __str__(self):
        return self.nom