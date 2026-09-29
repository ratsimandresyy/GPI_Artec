from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Limite les tentatives de connexion par adresse IP."""

    scope = "login"


class TicketCreateRateThrottle(AnonRateThrottle):
    """Limite les signalements anonymes (TicketPanne) par adresse IP."""

    scope = "ticket_create"
