from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts.models import User


class IsAdministrateur(BasePermission):
    """
    Accès réservé à un compte authentifié dont le rôle est ADMIN.

    Le JWT ne suffit pas : le rôle est vérifié côté serveur.
    """

    message = "Cette opération est réservée à l'administrateur."

    def has_permission(self, request, view):
        utilisateur = request.user

        return bool(
            utilisateur
            and utilisateur.is_authenticated
            and getattr(utilisateur, "role", None) == User.Role.ADMIN
        )


class IsAdministrateurOrReadOnly(BasePermission):
    """
    Lecture publique (mode visiteur) et écriture administrateur.

    À utiliser uniquement sur les ressources volontairement exposées
    au visiteur (équipements, localisation, bâtiments, etc.).
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return IsAdministrateur().has_permission(request, view)
