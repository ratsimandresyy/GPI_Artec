"""
Tests de securite de la representation des equipements (Etape 5).

Le mode visiteur ne doit pas recevoir les informations techniques
reservees a l'administration (numero de serie, adresses IP et MAC,
condition de stock). L'administrateur, lui, en a besoin sur les
memes endpoints de lecture.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from inventaire.models.batiment import Batiment
from inventaire.models.equipement import Equipement
from inventaire.models.etage import Etage
from inventaire.models.salle import Salle
from inventaire.serializers import (
    CHAMPS_EQUIPEMENT_ADMINISTRATION,
    CHAMPS_EQUIPEMENT_VISITEUR,
)


CHAMPS_RESERVES_ADMINISTRATION = (
    "numero_serie",
    "adresse_ip",
    "adresse_mac",
    "condition_stock",
    "fabricant",
    "modele",
)


class BaseEquipementsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_equipements",
            password="MotDePasseAdmin1",
            role=User.Role.ADMIN,
        )

        self.utilisateur = User.objects.create_user(
            username="user_equipements",
            password="MotDePasseUser1",
            role=User.Role.USER,
        )

        batiment = Batiment.objects.create(nom="Bâtiment Securite")

        etage = Etage.objects.create(
            batiment=batiment,
            numero=1,
            nom="RDC",
        )

        self.salle = Salle.objects.create(
            etage=etage,
            nom="Salle Securite",
        )

        self.equipement = Equipement.objects.create(
            nom="PC-SECURITE-01",
            type="ORDINATEUR",
            fabricant="Dell",
            modele="OptiPlex 7010",
            numero_inventaire="INV-SEC-01",
            numero_serie="SN-SECRET-123",
            adresse_ip="10.0.0.42",
            adresse_mac="AA:BB:CC:DD:EE:FF",
            etat="EN_SERVICE",
            situation="AFFECTE",
            condition_stock=None,
            salle=self.salle,
        )


class EquipementVisiteurTest(BaseEquipementsTest):
    """Mode visiteur : consultation complete, donnees techniques absentes."""

    def test_le_visiteur_peut_consulter_la_liste(self):
        response = self.client.get("/api/inventaire/equipements/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_le_visiteur_recoit_les_informations_de_consultation(self):
        response = self.client.get("/api/inventaire/equipements/")

        equipement = response.data[0]

        for champ in CHAMPS_EQUIPEMENT_VISITEUR:
            self.assertIn(champ, equipement)

        # Ces informations sont necessaires pour identifier et
        # localiser le materiel : elles doivent bien etre presentes.
        self.assertEqual(equipement["nom"], "PC-SECURITE-01")
        self.assertEqual(equipement["type"], "ORDINATEUR")
        self.assertEqual(equipement["numero_inventaire"], "INV-SEC-01")
        self.assertEqual(equipement["salle"], self.salle.id)
        self.assertEqual(equipement["etat"], "EN_SERVICE")
        self.assertEqual(equipement["situation"], "AFFECTE")

    def test_le_visiteur_ne_reçoit_pas_les_donnees_techniques(self):
        response = self.client.get("/api/inventaire/equipements/")

        equipement = response.data[0]

        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, equipement)

        # Aucune trace de la valeur sensible dans la reponse JSON.
        contenu = str(response.data)
        for valeur in ("SN-SECRET-123", "10.0.0.42", "AA:BB:CC:DD:EE:FF", "Dell", "OptiPlex 7010"):
            self.assertNotIn(valeur, contenu)

    def test_le_visiteur_ne_reçoit_pas_les_donnees_techniques_en_detail(self):
        response = self.client.get(
            f"/api/inventaire/equipements/{self.equipement.id}/"
        )

        self.assertEqual(response.status_code, 200)

        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, response.data)

        # Verifier specifiquement fabricant et modele ne sont pas dans la reponse
        contenu = str(response.data)
        self.assertNotIn("Dell", contenu)
        self.assertNotIn("OptiPlex 7010", contenu)

    def test_la_recherche_ne_fuit_pas_non_plus_les_donnees_techniques(self):
        response = self.client.get(
            "/api/inventaire/equipements/rechercher/",
            {"q": "SECURITE"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, response.data[0])

        # Verifier specifiquement fabricant et modele ne sont pas dans la recherche
        contenu = str(response.data)
        self.assertNotIn("Dell", contenu)
        self.assertNotIn("OptiPlex 7010", contenu)

    def test_un_utilisateur_authentifie_non_admin_est_limite_autant(self):
        """
        Etre authentifie ne suffit pas a obtenir la representation
        complete : seul le role ADMIN y donne droit.
        """
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.get("/api/inventaire/equipements/")

        self.assertEqual(response.status_code, 200)

        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, response.data[0])

    def test_le_visiteur_ne_peut_pas_etendre_la_reponse_avec_fields(self):
        """Le parametre ?fields= ne doit pas contourner la restriction."""
        self.client.get(
            "/api/inventaire/equipements/",
            {"fields": ",".join(CHAMPS_EQUIPEMENT_ADMINISTRATION)},
        )

        response = self.client.get(
            f"/api/inventaire/equipements/{self.equipement.id}/",
            {"fields": "adresse_mac,adresse_ip,numero_serie,fabricant,modele"},
        )

        self.assertEqual(response.status_code, 200)

        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, response.data)

        self.assertNotIn("AA:BB:CC:DD:EE:FF", str(response.data))
        self.assertNotIn("Dell", str(response.data))
        self.assertNotIn("OptiPlex 7010", str(response.data))

    def test_un_lecteur_seul_ne_peut_pas_ecrire(self):
        """La representation publique n'est jamais acceptee en ecriture."""
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.patch(
            f"/api/inventaire/equipements/{self.equipement.id}/",
            {"nom": "PC renomme"},
            format="json",
        )

        self.assertEqual(response.status_code, 403)

        self.equipement.refresh_from_db()
        self.assertEqual(self.equipement.nom, "PC-SECURITE-01")


class EquipementAdministrateurTest(BaseEquipementsTest):
    """L'administrateur conserve les informations necessaires a son travail."""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.admin)

    def test_l_administrateur_recoit_tous_les_champs_en_liste(self):
        response = self.client.get("/api/inventaire/equipements/")

        self.assertEqual(response.status_code, 200)

        equipement = response.data[0]

        for champ in CHAMPS_EQUIPEMENT_ADMINISTRATION:
            self.assertIn(champ, equipement)

        self.assertEqual(equipement["numero_serie"], "SN-SECRET-123")
        self.assertEqual(equipement["adresse_ip"], "10.0.0.42")
        self.assertEqual(equipement["adresse_mac"], "AA:BB:CC:DD:EE:FF")
        self.assertEqual(equipement["fabricant"], "Dell")
        self.assertEqual(equipement["modele"], "OptiPlex 7010")

    def test_l_administrateur_recoit_tous_les_champs_en_detail(self):
        response = self.client.get(
            f"/api/inventaire/equipements/{self.equipement.id}/"
        )

        self.assertEqual(response.status_code, 200)

        for champ in CHAMPS_EQUIPEMENT_ADMINISTRATION:
            self.assertIn(champ, response.data)

    def test_l_administrateur_peut_ecrire_les_donnees_techniques(self):
        response = self.client.patch(
            f"/api/inventaire/equipements/{self.equipement.id}/",
            {
                "adresse_mac": "11:22:33:44:55:66",
                "adresse_ip": "10.0.0.99",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.equipement.refresh_from_db()
        self.assertEqual(self.equipement.adresse_mac, "11:22:33:44:55:66")
        self.assertEqual(self.equipement.adresse_ip, "10.0.0.99")

    def test_l_administrateur_peut_creer_un_equipement_complet(self):
        response = self.client.post(
            "/api/inventaire/equipements/",
            {
                "nom": "PC-ADMIN-02",
                "type": "ORDINATEUR",
                "numero_inventaire": "INV-SEC-02",
                "numero_serie": "SN-ADMIN-456",
                "adresse_ip": "10.0.0.77",
                "adresse_mac": "AB:CD:EF:12:34:56",
                "fabricant": "HP",
                "modele": "EliteBook 840",
                "situation": "EN_STOCK",
                "condition_stock": "OCCASION",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["adresse_mac"], "AB:CD:EF:12:34:56")
        self.assertEqual(response.data["fabricant"], "HP")
        self.assertEqual(response.data["modele"], "EliteBook 840")


class SeparationChampsTest(TestCase):
    """Garde-fou sur la definition meme des deux listes de champs."""

    def test_les_champs_reserves_ne_sont_pas_publics(self):
        for champ in CHAMPS_RESERVES_ADMINISTRATION:
            self.assertNotIn(champ, CHAMPS_EQUIPEMENT_VISITEUR)
            self.assertIn(champ, CHAMPS_EQUIPEMENT_ADMINISTRATION)

    def test_la_representation_publique_est_un_sous_ensemble(self):
        self.assertTrue(
            set(CHAMPS_EQUIPEMENT_VISITEUR).issubset(
                set(CHAMPS_EQUIPEMENT_ADMINISTRATION)
            )
        )

    def test_les_champs_publiques_necessaires_sont_conserves(self):
        """Le visiteur doit pouvoir identifier et localiser le materiel."""
        for champ in (
            "id",
            "nom",
            "type",
            "numero_inventaire",
            "salle",
            "etat",
            "situation",
        ):
            self.assertIn(champ, CHAMPS_EQUIPEMENT_VISITEUR)

    def test_les_listes_ne_cachent_aucun_champ_du_modele(self):
        # concrete_fields = colonnes reelles, hors relations inversees
        # ("position", "tickets_panne", ...) qui ne sont pas serialisables.
        champs_modele = {
            champ.name for champ in Equipement._meta.concrete_fields
        }

        self.assertEqual(
            set(CHAMPS_EQUIPEMENT_ADMINISTRATION),
            champs_modele,
            "La liste d'administration doit couvrir tout le modele.",
        )
