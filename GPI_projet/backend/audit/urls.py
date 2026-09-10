from rest_framework.routers import DefaultRouter
from .views import (RapportAuditViewSet, ConnexionAuditViewSet)

router = DefaultRouter()

router.register("rapports", RapportAuditViewSet, basename = "rapport-audit")
router.register("connexions", ConnexionAuditViewSet, basename = "connexion-audit")
urlpatterns = router.urls