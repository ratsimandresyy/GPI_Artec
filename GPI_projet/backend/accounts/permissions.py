from rest_framework.permissions import BasePermission

class IsAdministrateurOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        # Permission publique
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True 

        # Permission reservee aux administrateurs
        return( request.user and request.user.is_authenticated and request.user.role == "ADMIN")

class IsUserOrAdministrateur(BasePermission):
        def has_permission(self, request, view):
            return ( request.user and request.user.is_authenticated and request.user.role in ("USER", "ADMIN"))