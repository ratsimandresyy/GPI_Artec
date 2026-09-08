from django.contrib import admin
from .models import RapportAudit,ConnexionAudit

# Register your models here.
@admin.register(RapportAudit)
class RapportAuditAdmin(admin.ModelAdmin):
    list_display = (
        "equipement",
        "date_audit",
        "system_exploitation",
        "processeur",
    )

    list_filter = (
        "date_audit",
        "system_exploitation",
    )

    search_fields = (
        "equipement_nom",
        "equipement_numero_inventaire",
    )

@admin.register(ConnexionAudit)
class ConnexionAuditAdmin(admin.ModelAdmin):
    list_display = (
        "equipement",
        "utilisateur",
        "date_connexion",
    )

    list_filter = (
        "date_connexion",
    )

    search_fields = (
        "equipement_nom",
        "nom_utilisateur",
    )