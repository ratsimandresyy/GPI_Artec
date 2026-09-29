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
from .services.localisation_service import LocalisationService

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


# Inventaire complet d'un equipement, reserve a l'administration.
#
# La liste est ecrite explicitement (et non "__all__") afin que le
# parametre de requete DRF "?fields=" ne puisse pas etendre la
# reponse a des champs non prvus ici.
CHAMPS_EQUIPEMENT_ADMINISTRATION = (
    "id",
    "nom",
    "type",
    "fabricant",
    "modele",
    "numero_inventaire",
    "numero_serie",
    "adresse_ip",
    "adresse_mac",
    "salle",
    "etat",
    "situation",
    "condition_stock",
)

# Donnees strictement necessaires au mode visiteur : identifier un
# materiel (nom, type, numero d'inventaire) et le localiser (salle, etat, situation).
#
# Les informations techniques d'inventaire et de reseau
# (numero_serie, adresse_ip, adresse_mac, fabricant, modele) et la condition de stock
# ne sont pas utiles a un visiteur : elles restent reservees a
# l'administration.
CHAMPS_EQUIPEMENT_VISITEUR = (
    "id",
    "nom",
    "type",
    "numero_inventaire",
    "salle",
    "etat",
    "situation",
)


class EquipementPublicSerializer(serializers.ModelSerializer):
    """
    Consultation d'un equipement par le visiteur (mode public).

    Lecture seule : cette representation ne sert qu'a l'affichage.
    Elle ne doit jamais etre utilisee pour valider une ecriture.
    """

    class Meta:
        model = Equipement
        fields = CHAMPS_EQUIPEMENT_VISITEUR
        read_only_fields = CHAMPS_EQUIPEMENT_VISITEUR


class EquipementSerializer(serializers.ModelSerializer):
    """
    Gestion d'un equipement par l'administration.

    Seul serializeur autorise a valider une ecriture : il porte les
    regles de stock et declenche le positionnement automatique.
    """

    class Meta:
        model = Equipement
        fields = CHAMPS_EQUIPEMENT_ADMINISTRATION

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

        if situation == "EN_STOCK" and salle:
            raise serializers.ValidationError({
                "salle": (
                    "Un matériel en stock ne peut pas être affecté "
                    "à une salle."
                )
            })

        if situation == "AFFECTE":
            attrs["condition_stock"] = None

        #RG-E03 : une chaîne vide n'est pas un numéro de série. Elle est
        #normalisée en NULL pour que plusieurs matériels sans numéro de
        #série puissent être enregistrés.
        if "numero_serie" in attrs and not attrs["numero_serie"]:
            attrs["numero_serie"] = None

        return attrs

    def create(self, validated_data):
        equipement = super().create(validated_data)

        # Attribuer une salle doit placer le materiel sur le plan,
        # sinon il reste invisible dans la vue Localisation.
        LocalisationService.positionner_si_affecte(equipement)

        return equipement

    def update(self, instance, validated_data):
        equipement = super().update(instance, validated_data)

        # Un changement de salle deplace le materiel sur le plan
        # de l'etage correspondant.
        LocalisationService.positionner_si_affecte(equipement)

        return equipement

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
            "titre",
            "type",
            "priorite",
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