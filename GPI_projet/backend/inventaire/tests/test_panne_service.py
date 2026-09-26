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
            titre="Panne écran",
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

        #Vérifie le titre
        self.assertEqual(
            ticket.titre,
            "Panne écran",
        )

        #Vérifie la description
        self.assertEqual(
            ticket.description,
            "L'écran ne s'allume plus.",
        )

        #Vérifie le type par défaut
        self.assertEqual(
            ticket.type,
            "MAINTENANCE",
        )

        #Vérifie la priorité par défaut
        self.assertEqual(
            ticket.priorite,
            "NORMALE",
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
            titre="Panne écran",
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
            titre="Panne écran",
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

    def test_declarer_panne_avec_type_et_priorite(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Réclamation utilisateur",
            description="L'utilisateur se plaint de la lenteur.",
            type="RECLAMATION",
            priorite="HAUTE",
        )

        self.assertEqual(
            ticket.type,
            "RECLAMATION",
        )

        self.assertEqual(
            ticket.priorite,
            "HAUTE",
        )

    def test_titre_obligatoire(self):
        with self.assertRaises(ValueError) as context:
            PanneService.declarer_panne(
                equipement=self.equipement,
                titre="",
                description="Description test",
            )

        self.assertIn(
            "titre",
            str(context.exception).lower(),
        )

    def test_qualifier_ticket(self):
        """
        Diagramme d'activité : "Qualifier le ticket : définir le type,
        définir la priorité".
        """
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        PanneService.qualifier_ticket(
            ticket,
            type="RECLAMATION",
            priorite="CRITIQUE",
        )

        ticket.refresh_from_db()

        self.assertEqual(ticket.type, "RECLAMATION")
        self.assertEqual(ticket.priorite, "CRITIQUE")

    def test_qualifier_ticket_avec_un_seul_champ(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        PanneService.qualifier_ticket(ticket, priorite="HAUTE")

        ticket.refresh_from_db()

        self.assertEqual(ticket.type, "MAINTENANCE")
        self.assertEqual(ticket.priorite, "HAUTE")

    def test_qualifier_ticket_sans_donnee_est_refuse(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        with self.assertRaises(ValueError):
            PanneService.qualifier_ticket(ticket)

    def test_qualifier_ticket_avec_valeurs_invalides(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        with self.assertRaises(ValueError):
            PanneService.qualifier_ticket(ticket, type="INCONNU")

        with self.assertRaises(ValueError):
            PanneService.qualifier_ticket(ticket, priorite="URGENT")

    def test_qualifier_ticket_ne_change_pas_le_statut(self):
        """
        La qualification ne remplace pas le workflow : le statut reste
        piloté par prendre_en_charge / resoudre_ticket.
        """
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        PanneService.qualifier_ticket(ticket, priorite="HAUTE")

        ticket.refresh_from_db()

        self.assertEqual(ticket.statut, "OUVERT")

    def test_resoudre_ticket_en_hors_service(self):
        """
        Diagramme d'activité : "Matériel réparé ?" Non -> HORS_SERVICE.
        """
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne carte mère",
            description="Le matériel ne démarre plus.",
        )

        PanneService.prendre_en_charge(ticket)

        PanneService.resoudre_ticket(
            ticket,
            "Carte mère défectueuse, matériel non réparable.",
            etat_final="HORS_SERVICE",
        )

        ticket.refresh_from_db()
        self.equipement.refresh_from_db()

        self.assertEqual(ticket.statut, "RESOLU")
        self.assertIsNotNone(ticket.date_resolution)
        self.assertEqual(self.equipement.etat, "HORS_SERVICE")

    def test_resoudre_ticket_avec_etat_final_invalide(self):
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        PanneService.prendre_en_charge(ticket)

        with self.assertRaises(ValueError):
            PanneService.resoudre_ticket(
                ticket,
                "Etat final impossible.",
                etat_final="EN_PANNE",
            )

        ticket.refresh_from_db()

        self.assertEqual(ticket.statut, "EN_COURS")

    def test_resoudre_ticket_sans_etat_final_remet_en_service(self):
        """
        Comportement par défaut conservé : sans état final fourni, le
        matériel est remis en service.
        """
        ticket = PanneService.declarer_panne(
            equipement=self.equipement,
            titre="Panne écran",
            description="L'écran ne s'allume plus.",
        )

        PanneService.prendre_en_charge(ticket)
        PanneService.resoudre_ticket(ticket, "Ecran remplacé.")

        ticket.refresh_from_db()
        self.equipement.refresh_from_db()

        self.assertEqual(ticket.statut, "RESOLU")
        self.assertEqual(self.equipement.etat, "EN_SERVICE")