from django.db import models

from inventaire.models.equipement import Equipement
# Create your models here.

class RapportAudit(models.Model):
   equipement = models.ForeignKey(
      Equipement,
      on_delete=models.CASCADE,
      related_name="rapports_audit",
      null = True,
      blank = True,
   )

   date_audit = models.DateTimeField(
      null = True,
      blank = True,
   )

   system_exploitation = models.CharField(
      max_length=255,
      blank=True,
   )

   processeur = models.CharField(
      max_length=255,
      blank=True,
   )

   memoire = models.CharField(
      max_length=255,
      blank=True,
   )

   stockage = models.CharField(
      max_length=100,
      blank=True,
   )

   bios = models.TextField(
      blank=True,
   )

   donnees_brutes = models.JSONField(
      default=dict,
      blank=True,
   )

   def __str__(self):
      return (
         f"Audit de {self.equipement.nom if self.equipement else 'équipement inconnu'} "
         f"du {self.date_audit}"
      )