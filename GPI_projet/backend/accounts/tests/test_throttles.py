"""
Tests du rate limiting (Etape 4).

Aucune dependance supplementaire n'est introduite : la protection
repose sur les throttles DRF deja presentes dans le projet
(accounts/throttles.py) et sur les plafonds declares dans
config/settings.py.

DRF lit DEFAULT_THROTTLE_RATES au moment du chargement du module :
override_settings ne modifierait donc pas le comportement reel. Les
tests ci-dessous lisent le plafond configure et declenchent
effectivement le blocage, ce qui valide la configuration livree.
"""

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventaire.models.equipement import Equipement
from inventaire.models.ticket_panne import TicketPanne
from inventaire.views import TicketPanneViewSet


def plafond(scope):
    """
    Nombre de requetes autorisees dans la fenetre du scope.

    Les rates DRF s'ecrivent "nombre/periode" ("5/min", "10/hour").
    """
    quantite, periode = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"][scope].split("/")

    durees = {"s": 1, "m": 60, "h": 3600, "d": 86400}

    assert periode[0] in durees, (
        f"Periode de throttle non geree pour le scope '{scope}' : {periode}"
    )

    return int(quantite)


class ConfigurationThrottleTest(TestCase):
    """Garde-fou : les deux scopes de protection doivent exister."""

    def test_les_plafonds_de_protection_sont_declares(self):
        plafonds = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]

        self.assertIn("login", plafonds)
        self.assertIn("ticket_create", plafonds)

    def test_le_login_est_throttle(self):
        from accounts.views import LoginView

        self.assertTrue(LoginView.throttle_classes)

    def test_la_creation_de_ticket_est_throttlee(self):
        vue = TicketPanneViewSet()
        vue.action = "create"
        vue.request = None

        self.assertTrue(vue.get_throttles())

    def test_la_consultation_des_tickets_n_est_pas_throttlee(self):
        """
        Le plafond protege la creation abusive, pas la consultation
        administrative : un administrateur lisant ses tickets ne doit
        pas etre bloque.
        """
        vue = TicketPanneViewSet()
        vue.action = "list"
        vue.request = None

        self.assertEqual(vue.get_throttles(), [])


class LoginThrottleTest(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        User.objects.create_user(
            username="admin_throttle",
            password="MotDePasseAdmin1",
            role=User.Role.ADMIN,
        )

    def _tenter(self, mot_de_passe="MotDePasseIncorrect1"):
        return self.client.post(
            "/api/auth/login/",
            {
                "username": "admin_throttle",
                "password": mot_de_passe,
            },
            format="json",
        )

    def test_les_tentatives_sont_bloquees_au_dela_du_plafond(self):
        autorisees = plafond("login")

        for _ in range(autorisees):
            self.assertEqual(self._tenter().status_code, 401)

        self.assertEqual(self._tenter().status_code, 429)

    def test_le_blocage_ne_fuit_rien_au_client(self):
        autorisees = plafond("login")

        for _ in range(autorisees + 1):
            bloquee = self._tenter()

        self.assertEqual(bloquee.status_code, 429)
        self.assertNotIn("access", bloquee.data)
        self.assertNotIn("refresh", bloquee.data)

    def test_une_serie_de_mots_de_passe_est_coupee(self):
        """Le brute force classique est interrompu par le plafond."""
        autorisees = plafond("login")

        for indice in range(autorisees + 1):
            self._tenter(mot_de_passe=f"EssaiMotDePasse{indice}")

        self.assertEqual(self._tenter().status_code, 429)


class TicketCreateThrottleTest(TestCase):

    def setUp(self):
        cache.clear()
        self.client = APIClient()

        # PanneService marque l'equipement EN_PANNE : chaque signalement
        # a besoin de son propre materiel.
        self.equipements = [
            Equipement.objects.create(
                nom=f"PC-THROTTLE-{indice}",
                type="ORDINATEUR",
                numero_inventaire=f"INV-THROTTLE-{indice}",
                etat="EN_SERVICE",
                situation="AFFECTE",
            )
            for indice in range(plafond("ticket_create") + 1)
        ]

    def _signaler(self, equipement):
        return self.client.post(
            "/api/inventaire/tickets-panne/",
            {
                "equipement": equipement.id,
                "titre": "Ecran noir",
                "description": "L'ecran ne s'allume plus.",
                "priorite": "NORMALE",
            },
            format="json",
        )

    def test_les_signalements_sont_bloques_au_dela_du_plafond(self):
        autorisees = plafond("ticket_create")

        for equipement in self.equipements[:autorisees]:
            self.assertEqual(self._signaler(equipement).status_code, 201)

        self.assertEqual(
            self._signaler(self.equipements[autorisees]).status_code,
            429,
        )

    def test_le_ticket_refuse_n_est_pas_enregistre(self):
        autorisees = plafond("ticket_create")

        for equipement in self.equipements[:autorisees]:
            self._signaler(equipement)

        self._signaler(self.equipements[autorisees])

        self.assertEqual(TicketPanne.objects.count(), autorisees)

    def test_un_administrateur_authentifie_n_est_pas_bloque(self):
        """
        AnonRateThrottle laisse passer un utilisateur authentifie :
        le plafond protege l'usage anonyme (le visiteur) et n'entrave
        pas le traitement administrateur des tickets.
        """
        admin = User.objects.create_user(
            username="admin_sans_plafond",
            password="MotDePasseAdmin1",
            role=User.Role.ADMIN,
        )

        self.client.force_authenticate(user=admin)

        for _ in range(plafond("ticket_create") + 2):
            self.client.post(
                "/api/inventaire/tickets-panne/",
                {
                    "equipement": self.equipements[0].id,
                    "titre": "Consultation admin",
                    "description": "Traitement par l'administration.",
                    "priorite": "HAUTE",
                },
                format="json",
            )

        self.assertEqual(
            self.client.get(
                "/api/inventaire/tickets-panne/"
            ).status_code,
            200,
        )
