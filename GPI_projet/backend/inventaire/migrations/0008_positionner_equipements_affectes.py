from django.db import migrations

# Dimensions utilisees par PlanViewer lorsque le plan ne declare
# ni largeur ni hauteur.
LARGEUR_PAR_DEFAUT = 1000
HAUTEUR_PAR_DEFAUT = 700


def positionner_equipements_affectes(apps, schema_editor):
    """
    Place sur le plan les materiels deja affectes a une salle.

    Avant cette migration, attribuer une salle ne creait aucune Position :
    les materiels restaient invisibles dans la vue Localisation.
    """

    Equipement = apps.get_model("inventaire", "Equipement")
    Plan = apps.get_model("inventaire", "Plan")
    Position = apps.get_model("inventaire", "Position")

    for equipement in Equipement.objects.filter(
        situation="AFFECTE"
    ).exclude(salle=None).select_related("salle"):

        # Un etage n'a qu'un seul plan.
        plan = Plan.objects.filter(
            etage_id=equipement.salle.etage_id
        ).first()

        if plan is None:
            continue

        position = Position.objects.filter(
            equipement=equipement
        ).first()

        # Un emplacement deja choisi est conserve.
        if position is not None and position.plan_id == plan.id:
            continue

        x = (plan.largeur or LARGEUR_PAR_DEFAUT) / 2
        y = (plan.hauteur or HAUTEUR_PAR_DEFAUT) / 2

        Position.objects.update_or_create(
            equipement=equipement,
            defaults={
                "plan": plan,
                "x": x,
                "y": y,
            },
        )


def retirer_positions_obsoletes(apps, schema_editor):
    """
    Annule la migration : les positions creees sont supprimees,
    celles qui existaient deja sont conservees.
    """

    Equipement = apps.get_model("inventaire", "Equipement")
    Plan = apps.get_model("inventaire", "Plan")
    Position = apps.get_model("inventaire", "Position")

    for position in Position.objects.select_related("equipement"):

        equipement = position.equipement

        if equipement.situation != "AFFECTE" or equipement.salle is None:
            position.delete()
            continue

        plan = Plan.objects.filter(
            etage_id=equipement.salle.etage_id
        ).first()

        if plan is None or position.plan_id != plan.id:
            position.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("inventaire", "0007_alter_equipement_numero_serie"),
    ]

    operations = [
        migrations.RunPython(
            positionner_equipements_affectes,
            retirer_positions_obsoletes,
        ),
    ]