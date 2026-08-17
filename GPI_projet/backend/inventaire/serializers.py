from rest_framework import serializers
from .models import (
    Batiment,
    Etage,
    Salle,
    Equipement,
    Plan,
    Position,
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

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = "__all__"

class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"