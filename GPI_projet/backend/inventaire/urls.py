from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import(
    BatimentViewSet,
    EtageViewSet,
    SalleViewSet,
    EquipementViewSet,
    PlanViewSet,
    PositionViewSet,
)

router = DefaultRouter()

router.register(
    r"batiments",
    BatimentViewSet,
)

router.register(
    r"etages",
    EtageViewSet,
)

router.register(
    r"salles",
    SalleViewSet,
)

router.register(
    r"equipements",
    EquipementViewSet,
)

router.register(
    r"plans",
    PlanViewSet,
)

router.register(
    r"positions",
    PositionViewSet,
)

urlpatterns = [
    path("", include(router.urls)),
]
