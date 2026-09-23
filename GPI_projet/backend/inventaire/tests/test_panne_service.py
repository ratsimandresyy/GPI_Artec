from django.test import TestCase

from inventaire.models.equipement import Equipement
from inventaire.models.ticket_panne import TicketPanne
from inventaire.services.panne_service import PanneService

class PanneServiceTest(TestCase):
    def setUp(self):
        self.equipement = Equipement.objects.create(
            nom="PC-TEST-PANNE",
            type="ORDINATEUR",
            numero_inventaire="TEST-PANNE-001",
            numero_serie="SN-TEST-PANNE-001",
            etat="EN_SERVICE",
            situation="AFFECTE",
        )

    def test_declarer_panne(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            description="L'écran ne s'allume plus.",
        )

        #Vérifier l'état de l'équipement.
        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.etat,
            "EN_PANNE",
        )

        #La situation ne doit pas changer
        self.assertEqual(
            self.equipement.situation,
            "AFFECTE",
        )

        #Vérifie que le ticket a été crée
        self.assertEqual(
            TicketPanne.objects.count(),
            1,
        )

        #Vérifie que le ticket correspond au bon équipement.
        self.assertEqual(
            ticket.equipement,
            self.equipement,
        )

        #Vérifie la description
        self.assertEqual(
            ticket.description,
            "L'écran ne s'allume plus.",
        )

        #Un nouveau ticket doit être ouvert.
        self.assertEqual(
            ticket.statut,
            "OUVERT",
        )

        self.assertEqual(
            ticket.equipement,
            self.equipement,
        )

    def test_prendre_en_charge(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            description="L'écran ne s'allume plus."
        )

        PanneService.prendre_en_charge(ticket)

        ticket.refresh_from_db()

        self.assertEqual(
            ticket.statut,
            "EN_COURS",
        )

    def test_resoudre_ticket(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            description="L'écran ne s'affiche plus."
        )

        PanneService.prendre_en_charge(ticket)

        PanneService.resoudre_ticket(
            ticket,
            "Ecran remplacé et fonctionnel."
        )

        ticket.refresh_from_db()
        self.equipement.refresh_from_db()

        self.assertEqual(
            ticket.statut,
            "RESOLU",
        )

        self.assertIsNotNone(
            ticket.date_resolution,
        )

        self.assertEqual(
            ticket.commentaire_resolution,
            "Ecran remplacé et fonctionnel.",
        )

        self.assertEqual(
            self.equipement.etat,
            "EN_SERVICE",
        )

        #La situation physique reste inchngée.
        self.assertEqual(
            self.equipement.situation,
            "AFFECTE",
        )