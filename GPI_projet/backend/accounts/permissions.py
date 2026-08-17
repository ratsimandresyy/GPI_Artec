from rest_framework.permissions import BasePermission

class IsAdministrateurOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.methode in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == "ADMIN"