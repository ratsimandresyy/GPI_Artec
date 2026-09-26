from django.db import transaction

from inventaire.models.equipement import Equipement
from inventaire.models.position import Position
from inventaire.models.salle import Salle
from inventaire.models.plan import Plan


class LocalisationService:
    @staticmethod
    def _valider_localisation(
        equipement: Equipement,
        salle: Salle,
        plan: Plan,
        x: float,
        y: float,
    ):
        #Un equipement en stock ne peut pas etre localise.
        if equipement.situation != "AFFECTE":
            raise ValueError(
                "Seul un équipement affecté peut etre localisé."
            )

        #La salle doit appartenir au meme etage que le plan.
        if salle.etage_id != plan.etage_id:
            raise ValueError(
                "La salle et le plan doivent appartenir au même étage."
            )

         # Les coordonnées ne peuvent pas être négatives.
        if x < 0 or y < 0:
            raise ValueError(
                "Les coordonnées X et Y doivent être positives ou nulles."
            )

        # Vérification des limites du plan lorsque ses dimensions
        # sont disponibles.
        if plan.largeur is not None and x > plan.largeur:
            raise ValueError(
                "La coordonnée X dépasse la largeur du plan."
            )

        if plan.hauteur is not None and y > plan.hauteur:
            raise ValueError(
                "La coordonnée Y dépasse la hauteur du plan."
            )

    @staticmethod
    @transaction.atomic
    def localiser_equipement(
        equipement: Equipement,
        salle: Salle,
        plan: Plan,
        x: float,
        y: float,
    ) -> Position:
        """
        Crée ou met à jour la localisation d'un équipement.
        """

        LocalisationService._valider_localisation(
            equipement=equipement,
            salle=salle,
            plan=plan,
            x=x,
            y=y,
        )

        # L'équipement est affecté à la salle.
        equipement.salle = salle
        equipement.save(update_fields=["salle"])

        # Un équipement possède au maximum une position.
        position, _ = Position.objects.update_or_create(
            equipement=equipement,
            defaults={
                "plan": plan,
                "x": x,
                "y": y,
            },
        )

        return position

    @staticmethod
    @transaction.atomic
    def deplacer_equipement(
        equipement: Equipement,
        plan: Plan,
        x: float,
        y: float,
    ) -> Position:
        """
        Déplace un équipement déjà localisé vers une nouvelle
        position sur un plan.
        """

        try:
            position = equipement.position
        except Position.DoesNotExist:
            raise ValueError(
                "L'équipement n'a pas encore de localisation."
            )

        if equipement.salle is None:
            raise ValueError(
                "L'équipement doit être affecté à une salle."
            )

        if equipement.salle.etage_id != plan.etage_id:
            raise ValueError(
                "Le nouveau plan doit appartenir au même étage "
                "que la salle de l'équipement."
            )

        if x < 0 or y < 0:
            raise ValueError(
                "Les coordonnées X et Y doivent être positives ou nulles."
            )

        if plan.largeur is not None and x > plan.largeur:
            raise ValueError(
                "La coordonnée X dépasse la largeur du plan."
            )

        if plan.hauteur is not None and y > plan.hauteur:
            raise ValueError(
                "La coordonnée Y dépasse la hauteur du plan."
            )

        position.plan = plan
        position.x = x
        position.y = y

        position.save(
            update_fields=["plan", "x", "y"]
        )

        return position

    @staticmethod
    @transaction.atomic
    def retirer_localisation(equipement: Equipement):
        """
        Supprime la position graphique d'un équipement.
        """

        Position.objects.filter(
            equipement=equipement
        ).delete()