from rest_framework.test import APIClient

from django.test import TestCase

from accounts.models import User
from inventaire.models.equipement import Equipement
from inventaire.models.ticket_panne import TicketPanne
from inventaire.services.panne_service import PanneService


class TicketPermissionsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_tickets",
            password="MotDePasseAdmin1",
            role=User.Role.ADMIN,
        )

        self.equipement = Equipement.objects.create(
            nom="PC-TICKET-SEC",
            type="ORDINATEUR",
            numero_inventaire="INV-TICKET-SEC",
            etat="EN_SERVICE",
            situation="AFFECTE",
        )

    def test_visiteur_peut_creer_un_signalement(self):
        response = self.client.post(
            "/api/inventaire/tickets-panne/",
            {
                "equipement": self.equipement.id,
                "titre": "Écran noir",
                "description": "L'écran ne s'allume plus.",
                "type": "MAINTENANCE",
                "priorite": "NORMALE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["priorite"], "NORMALE")
        self.assertEqual(response.data["statut"], "OUVERT")

    def test_visiteur_ne_peut_pas_lister_les_tickets(self):
        PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Déjà déclaré",
            description="Description interne.",
        )

        response = self.client.get("/api/inventaire/tickets-panne/")
        self.assertEqual(response.status_code, 401)

    def test_visiteur_ne_peut_pas_consulter_un_ticket(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Ticket existant",
            description="Ne doit pas être lisible.",
        )

        response = self.client.get(
            f"/api/inventaire/tickets-panne/{ticket.id}/"
        )
        self.assertEqual(response.status_code, 401)

    def test_visiteur_ne_peut_pas_modifier_le_statut(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Statut",
            description="Tentative de modification.",
        )

        response = self.client.put(
            f"/api/inventaire/tickets-panne/{ticket.id}/",
            {"statut": "RESOLU"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

        ticket.refresh_from_db()
        self.assertEqual(ticket.statut, "OUVERT")

    def test_visiteur_ne_peut_pas_modifier_le_statut_en_patch(self):
        """PATCH (partial_update) doit etre bloque comme PUT."""
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Patch",
            description="Tentative de modification partielle.",
        )

        response = self.client.patch(
            f"/api/inventaire/tickets-panne/{ticket.id}/",
            {"statut": "RESOLU"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

        ticket.refresh_from_db()
        self.assertEqual(ticket.statut, "OUVERT")

    def test_visiteur_ne_peut_pas_supprimer_un_ticket(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Suppression",
            description="Interdit au visiteur.",
        )

        response = self.client.delete(
            f"/api/inventaire/tickets-panne/{ticket.id}/"
        )

        self.assertEqual(response.status_code, 401)
        self.assertTrue(
            TicketPanne.objects.filter(id=ticket.id).exists()
        )

    def test_visiteur_ne_peut_pas_qualifier_le_ticket(self):
        """La priorite CRITIQUE passe uniquement par l'action admin."""
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Qualification",
            description="Interdit au visiteur.",
            priorite="NORMALE",
        )

        response = self.client.post(
            f"/api/inventaire/tickets-panne/{ticket.id}/qualifier/",
            {"priorite": "CRITIQUE"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

        ticket.refresh_from_db()
        self.assertEqual(ticket.priorite, "NORMALE")

    def test_le_visiteur_ne_peut_pas_imposer_un_statut_a_la_creation(self):
        """Un statut envoye dans le corps de la requete est ignore."""
        response = self.client.post(
            "/api/inventaire/tickets-panne/",
            {
                "equipement": self.equipement.id,
                "titre": "Statut imposé",
                "description": "Le statut doit rester OUVERT.",
                "statut": "RESOLU",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["statut"], "OUVERT")

    def test_visiteur_ne_peut_pas_prendre_en_charge(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Prise en charge",
            description="Interdit au visiteur.",
        )

        response = self.client.post(
            f"/api/inventaire/tickets-panne/{ticket.id}/prendre-en-charge/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_visiteur_ne_peut_pas_cloturer(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Clôture",
            description="Interdit au visiteur.",
        )

        response = self.client.post(
            f"/api/inventaire/tickets-panne/{ticket.id}/resoudre/",
            {"commentaire_resolution": "fait"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_visiteur_ne_peut_pas_creer_une_priorite_critique(self):
        response = self.client.post(
            "/api/inventaire/tickets-panne/",
            {
                "equipement": self.equipement.id,
                "titre": "Critique refusée",
                "description": "Ne doit pas passer.",
                "priorite": "CRITIQUE",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(TicketPanne.objects.count(), 0)

    def test_administrateur_peut_lister_et_qualifier(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="À qualifier",
            description="Pour l'admin.",
            priorite="NORMALE",
        )

        self.client.force_authenticate(user=self.admin)

        liste = self.client.get("/api/inventaire/tickets-panne/")
        self.assertEqual(liste.status_code, 200)
        self.assertEqual(len(liste.data), 1)

        qualification = self.client.post(
            f"/api/inventaire/tickets-panne/{ticket.id}/qualifier/",
            {"priorite": "CRITIQUE"},
            format="json",
        )
        self.assertEqual(qualification.status_code, 200)
        self.assertEqual(qualification.data["priorite"], "CRITIQUE")

        prise = self.client.post(
            f"/api/inventaire/tickets-panne/{ticket.id}/prendre-en-charge/",
            {},
            format="json",
        )
        self.assertEqual(prise.status_code, 200)
        self.assertEqual(prise.data["statut"], "EN_COURS")
