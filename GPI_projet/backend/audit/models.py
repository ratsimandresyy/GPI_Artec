from django.db import models

# Create your models here.

class RapportAudit(models.Model):
    nom_fichier = models.CharField(
        max_length = 255,
        unique = True,
    )

    fichier = models.FileField(
        upload_to = "audits/",
    )

    date_importation = models.DateTimeField(
        auto_now_add = True,
    )

    traite = models.BooleanField(
        default = False,
    )

    def __str__(self):
        return self.nom_fichier