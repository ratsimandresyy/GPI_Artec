from rest_framework import serializers
from .models import RapportAudit, ConnexionAudit

class RapportAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = RapportAudit
        fields = "__all__"

class ConnexionAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConnexionAudit
        fields = "__all__"