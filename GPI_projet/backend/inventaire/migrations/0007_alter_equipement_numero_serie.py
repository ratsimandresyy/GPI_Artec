"""
RG-E03 : le numéro de série est unique lorsqu'il est renseigné.

La colonne devient nullable afin que plusieurs équipements sans numéro de
série puissent coexister : une chaîne vide viole la contrainte d'unicité,
alors qu'un NULL n'entre jamais en conflit (PostgreSQL autorise plusieurs
NULL dans une colonne UNIQUE).

Cette migration a été écrite à la main, Django n'étant pas installé dans
l'environnement utilisé ; elle reprend la structure produite par
makemigrations.
"""

from django.db import migrations, models


def chaines_vides_vers_null(apps, schema_editor):
    """Convertit en NULL les numéros de série vides déjà enregistrés."""
    equipement = apps.get_model("inventaire", "Equipement")
    equipement.objects.filter(numero_serie="").update(numero_serie=None)


class Migration(migrations.Migration):

    dependencies = [
        ('inventaire', '0006_ticketpanne_priorite_ticketpanne_titre_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='equipement',
            name='numero_serie',
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.RunPython(
            chaines_vides_vers_null,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
