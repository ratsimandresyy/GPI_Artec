from django.contrib import admin
from .models import RapportAudit

# Register your models here.
@admin.register(RapportAudit)
class RapportAuditAdmin(admin.ModelAdmin):
    list_display = (
        "nom_fichier",
        "date_importation",
        "traite",
    )

    list_filter = (
        "traite",
        "date_importation",
    )

    search_fields = (
        "nom_fichier",
    )