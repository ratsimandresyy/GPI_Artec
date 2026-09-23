from django.contrib import admin

from .models import (
    Batiment,
    Etage,
    Salle,
    Equipement,
    Plan,
    Position,
    TicketPanne
)
# Register your models here.

@admin.register(Batiment)
class BatimentAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "description",
        )
    search_fields = (
        "nom",
        )

@admin.register(Etage)
class EtageAdmin(admin.ModelAdmin):
    list_display = (
        "nom", 
        "numero", 
        "batiment",
        )
    list_filter = (
        "batiment",
        )
    search_fields = (
        "nom", 
        "batiment_nom",
        )

@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = (
        "nom", 
        "etage",
        )
    list_filter = (
        "etage",
        )
    search_fields = (
        "nom", 
        "etage_nom",
        )

@admin.register(Equipement)
class EquipementAdmin(admin.ModelAdmin):
    list_display = (
        "nom",
        "numero_inventaire",
        "type",
        "etat",
        "adresse_ip",
        "adresse_mac",
    )
    list_filter = (
        "type",
        "etat",
        "salle",
        "situation",
    )

    search_fields = (
        "nom",
        "numero_inventaire",
        "adresse_ip",
        "adresse_mac",
    )

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "etage",
        "image",
        "largeur",
        "hauteur",
    )
    list_filter = (
        "etage",
    )

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = (
        "equipement",
        "plan",
        "x",
        "y",
    )
    list_filter = (
        "plan",
    )

    search_fields = (
        "epquipement_nom",
        "equipement_numero_inventaire",
    )

@admin.register(TicketPanne)
class TicketPanneAdmin(admin.ModelAdmin):
    list_display = (
        "equipement",
        "date_signalement",
        "statut",
        "date_resolution",
    )

    list_filter = (
        "statut",
        "date_signalement",
    )

    search_fields = (
        "equipement__nom",
        "equipement__numero_invntaire",
        "description",
    )

    readonly_fields = (
        "date_signalement",
    )
