from django.db import transaction

from inventaire.models.equipement import Equipement
from inventaire.models.position import Position

class StockService:

    @staticmethod
    @transaction.atomic
    def transferer_vers_stock(equipement: Equipement, condition_stock: str) -> Equipement:
        if equipement.situation != "AFFECTE":
            raise ValueError(
                "Seul un équipement affecté peut être transféré vers le stock."
            )

        if condition_stock not in ("NEUF", "OCCASION", "RECONDITIONNE"):
            raise ValueError(
                "La condition du matériel doit être NEUF, OCCASION ou RECONDITIONNE."
            )

        equipement.situation = "EN_STOCK"
        equipement.etat = "EN_MAINTENANCE"

        # L'équipement n'est plus affecté à une salle.
        equipement.salle = None

        equipement.save(
            update_fields=["situation", "etat", "salle"]
        )

        # L'équipement ne doit plus avoir de position sur le plan s'il n'est plus dans une salle
        Position.objects.filter(
            equipement=equipement
        ).delete()

        return equipement

    @staticmethod
    @transaction.atomic
    def terminer_maintenance(equipement: Equipement) -> Equipement:
        if equipement.situation != "EN_STOCK":
            raise ValueError(
                "Seul un équipement en stock peut terminer sa maintenance."
            )

        if equipement.etat != "EN_MAINTENANCE":
            raise ValueError(
                "L'équipement doit être en maintenance pour terminer celle-ci."
            )

        equipement.etat = "EN_SERVICE"

        equipement.save(
            update_fields=["etat"]
        )

        return equipement

    @staticmethod
    @transaction.atomic
    def affecter_equipement(
        equipement: Equipement,
        salle,
        plan,
        x: float,
        y: float,
    ) -> Equipement:
        if equipement.situation != "EN_STOCK":
            raise ValueError(
                "Seul un équipement en stock peut être affecté."
            )

        if equipement.etat != "EN_SERVICE":
            raise ValueError(
                "Seul un équipement en service peut être affecté."
            )

        equipement.situation = "AFFECTE"
        equipement.condition_stock = None
        equipement.etat = "EN_SERVICE"
        equipement.salle = salle

        equipement.save(
            update_fields=["situation", "etat", "salle","condition_stock"]
        )

        Position.objects.update_or_create(
            equipement = equipement,
            defaults={
                "plan": plan,
                "x" : x,
                "y" : y,
            },
        )

        return equipement
