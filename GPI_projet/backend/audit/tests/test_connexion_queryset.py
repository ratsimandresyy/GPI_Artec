"""
Tests de performance de l'endpoint des connexions (Etape 5).

ConnexionAuditViewSet utilise select_related sur ses deux cles
etrangeres. Ces tests verifient que cette optimisation porte bien sur
des relations reelles du modele, qu'elle est effectivement appliquee
par le SQL genere, et que la serialisation ne provoque pas de requete
supplementaire par enregistrement.
"""

from django.core.exceptions import FieldError
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from accounts.models import User
from audit.models import ConnexionAudit
from audit.views import ConnexionAuditViewSet
from inventaire.models.equipement import Equipement


class ConnexionAuditSelectRelatedTest(TestCase):

    def test_select_related_utilise_les_relations_existantes(self):
        """Aucune relation citee ne doit etre inexistante."""
        champ_equipement = ConnexionAudit._meta.get_field("equipement")
        champ_utilisateur = ConnexionAudit._meta.get_field("utilisateur")

        self.assertTrue(champ_equipement.is_relation)
        self.assertTrue(champ_utilisateur.is_relation)

        try:
            str(ConnexionAuditViewSet.queryset.query)
        except FieldError:
            self.fail(
                "select_related de ConnexionAuditViewSet référence "
                "un champ inexistant."
            )

    def test_select_related_couvre_les_deux_cles_etrangeres(self):
        relations = ConnexionAuditViewSet.queryset.query.select_related

        self.assertTrue(relations, "select_related n'est pas appliqué.")
        self.assertIn("equipement", relations)
        self.assertIn("utilisateur", relations)

    def test_le_sql_genere_contient_les_jointures(self):
        sql = str(ConnexionAuditViewSet.queryset.query)

        self.assertIn("JOIN", sql)
        self.assertIn(ConnexionAudit._meta.get_field("equipement").related_model._meta.db_table, sql)
        self.assertIn(ConnexionAudit._meta.get_field("utilisateur").related_model._meta.db_table, sql)


class ConnexionAuditQueriesTest(TestCase):
    """Absence de N+1 sur la liste des connexions."""

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_audit_queries",
            password="MotDePasseAdmin1",
            role=User.Role.ADMIN,
        )

        self.client.force_authenticate(user=self.admin)

    def _creer_connexions(self, nombre, decalage=0):
        for indice in range(nombre):
            equipement = Equipement.objects.create(
                nom=f"PC-AUDIT-{decalage}-{indice}",
                type="ORDINATEUR",
                numero_inventaire=f"INV-AUDIT-{decalage}-{indice}",
                situation="AFFECTE",
                etat="EN_SERVICE",
            )

            ConnexionAudit.objects.create(
                equipement=equipement,
                utilisateur=self.admin,
                nom_utilisateur=f"DOMAINE\\utilisateur{decalage}{indice}",
            )

    def test_le_nombre_de_requetes_ne_croit_pas_avec_les_donnees(self):
        self._creer_connexions(3)

        with CaptureQueriesContext(connection) as premier:
            response = self.client.get("/api/audit/connexions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)

        self._creer_connexions(5, decalage=10)

        with CaptureQueriesContext(connection) as second:
            response = self.client.get("/api/audit/connexions/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 8)
        self.assertEqual(
            len(premier.captured_queries),
            len(second.captured_queries),
            "La liste des connexions sufferait d'un N+1.",
        )
