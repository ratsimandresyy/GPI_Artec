from django.db import models
from inventaire.models.equipement import Equipement
from accounts.models import User

class ConnexionAudit(models.Model):
    equipement = models.ForeignKey(Equipement,
                                   on_delete=models.CASCADE,
                                   related_name="connexions",)

    utilisateur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="connexions",
    )

    nom_utilisateur =models.CharField(max_length=150,)

    date_connexion = models.DateField(
        auto_now_add=True,
    )

    def __str__(self):
        return(
            f"{self.nom_utilisateur} - "
            f"{self.equipement.nom} - "
            f"{self.date_connexion}"
        )