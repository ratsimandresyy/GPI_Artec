from rest_framework import serializers
from .models import RapportAudit, ConnexionAudit

class RapportAuditSerializer(serializers.ModelSerializer):
    equipement_nom = serializers.CharField(
        source="equipement.nom",
        read_only=True,
    )

    numero_inventaire = serializers.CharField(
        source="equipement.numero_inventaire",
        read_only=True,
    )

    class Meta:
        model = RapportAudit
        fields = [
            "id",
            "equipement",
            "equipement_nom",
            "numero_inventaire",
            "date_audit",
            "system_exploitation",
            "processeur",
            "memoire",
            "stockage",
            "bios",
            "donnees_brutes",
        ]

class ConnexionAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnexionAudit
        fields = "__all__"