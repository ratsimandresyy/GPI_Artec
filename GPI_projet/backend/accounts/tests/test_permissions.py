from rest_framework.test import APIClient

from django.test import TestCase

from accounts.models import User


class AuthentificationPermissionsTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin_gpi",
            password="MotDePasseAdmin1",
            email="admin@example.com",
            role=User.Role.ADMIN,
        )

        self.utilisateur = User.objects.create_user(
            username="user_gpi",
            password="MotDePasseUser1",
            email="user@example.com",
            role=User.Role.USER,
        )

    def test_visiteur_peut_consulter_les_equipements(self):
        response = self.client.get("/api/inventaire/equipements/")
        self.assertEqual(response.status_code, 200)

    def test_visiteur_refuse_sur_liste_utilisateurs(self):
        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, 401)

    def test_visiteur_refuse_sur_me(self):
        response = self.client.get("/api/auth/users/me/")
        self.assertEqual(response.status_code, 401)

    def test_visiteur_refuse_sur_audits(self):
        response = self.client.get("/api/audit/rapports/")
        self.assertEqual(response.status_code, 401)

    def test_utilisateur_refuse_sur_endpoints_admin(self):
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/inventaire/batiments/",
            {"nom": "Bâtiment interdit"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_administrateur_accede_aux_utilisateurs(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 2)

    def test_login_refuse_un_compte_non_admin(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "user_gpi",
                "password": "MotDePasseUser1",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertNotIn("access", response.data)

    def test_login_accepte_un_administrateur(self):
        response = self.client.post(
            "/api/auth/login/",
            {
                "username": "admin_gpi",
                "password": "MotDePasseAdmin1",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["role"], User.Role.ADMIN)


class UtilisateursSecuriteTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.utilisateur = User.objects.create_user(
            username="user_profil",
            password="MotDePasseUser1",
            email="profil@example.com",
            role=User.Role.USER,
        )

        self.autre = User.objects.create_user(
            username="autre_user",
            password="MotDePasseUser2",
            role=User.Role.USER,
        )

    def test_visiteur_ne_peut_pas_lister_les_comptes(self):
        response = self.client.get("/api/auth/users/")
        self.assertEqual(response.status_code, 401)

    def test_me_retourne_uniquement_l_utilisateur_authentifie(self):
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.get("/api/auth/users/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.utilisateur.id)
        self.assertEqual(response.data["username"], "user_profil")
        self.assertNotEqual(response.data["id"], self.autre.id)

    def test_utilisateur_ne_peut_pas_modifier_son_role(self):
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.put(
            "/api/auth/users/me/",
            {
                "username": "user_profil",
                "email": "profil@example.com",
                "role": "ADMIN",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.utilisateur.refresh_from_db()
        self.assertEqual(self.utilisateur.role, User.Role.USER)

    def test_utilisateur_ne_devient_pas_admin_par_http(self):
        self.client.force_authenticate(user=self.utilisateur)

        response = self.client.put(
            "/api/auth/users/me/",
            {"role": User.Role.ADMIN},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.utilisateur.refresh_from_db()
        self.assertEqual(self.utilisateur.role, User.Role.USER)
