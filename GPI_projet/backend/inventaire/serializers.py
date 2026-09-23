from rest_framework import serializers
from .models import (
    Batiment,
    Etage,
    Salle,
    Equipement,
    Plan,
    Position,
    TicketPanne
)

class BatimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batiment
        fields = "__all__"

class EtageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Etage
        fields = "__all__"

class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = "__all__"

class EquipementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipement
        fields = "__all__"

    def validate(self, attrs):
        situation = attrs.get(
            "situation",
            getattr(self.instance, "situation", None)
        )

        condition_stock = attrs.get(
            "condition_stock",
            getattr(self.instance, "condition_stock", None)
        )

        salle = attrs.get(
            "salle",
            getattr(self.instance, "salle", None)
    )

        if situation == "EN_STOCK" and not condition_stock:
            raise serializers.ValidationError({
                "condition_stock": (
                    "La condition du materiel doit être renseignée lorsqu'il est en stock."
                )
            })

        if salle:
            raise serializers.ValidationError({
                "salle": (
                    "Un matériel en stock ne peut pas être affecté "
                    "à une salle."
                )
            })

        if situation == "AFFECTE":
            attrs["condition_stock"] = None

        return attrs

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"

class PositionDetailSerializer(serializers.ModelSerializer):
    #detaille de la localisation
    equipement_nom = serializers.CharField(
        source="equipement.nom",
        read_only=True,
    )
    numero_inventaire = serializers.CharField(
        source = "equipement.numero_inventaire",
        read_only = True,
    )
    plan_image = serializers.ImageField(
        source = "plan.image",
        read_only = True,
    )
    class Meta:
        model = Position
        fields = [
            "id",
            "equipement",
            "equipement_nom",
            "numero_inventaire",
            "plan",
            "plan_image",
            "x",
            "y",
        ]

class TicketPanneSerializer(serializers.ModelSerializer):
    equipement_nom = serializers.CharField(
        source="equipement.nom",
        read_only = True,
    )

    numero_inventaire = serializers.CharField(
        source = "equipement.numero_inventaire",
        read_only = True,
    )

    class Meta:
        model = TicketPanne
        fields = [
            "id",
            "equipement",
            "equipement_nom",
            "numero_inventaire",
            "date_signalement",
            "description",
            "statut",
            "date_resolution",
            "commentaire_resolution",
        ]

        read_only_fields = [
            "id",
            "date_signalement",
            "equipement_nom",
            "numero_inventaire",
            "statut",
            "date_resolution",
            "commentaire_resolution",
        ]