from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    "Configuration de l'affichage du User perso dans Django"

    fieldsets = UserAdmin.fieldsets + (
        (
            "GPI",
            {
                "fields": ("role",),
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "GPI",
            {
                "fields": ("role",),
            },
        ),
    )
