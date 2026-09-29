from django.test import TestCase

from inventaire.models.batiment import Batiment
from inventaire.models.etage import Etage
from inventaire.models.plan import Plan
from inventaire.models.salle import Salle
from inventaire.models.equipement import Equipement
from inventaire.models.position import Position

from inventaire.services.localisation_service import LocalisationService


class LocalisationServiceTest(TestCase):
    """
    Tests des règles métier liées à la localisation
    des équipements.
    """

    def setUp(self):
        # Bâtiment
        self.batiment = Batiment.objects.create(
            nom="Bâtiment A"
        )

        # Deux étages
        self.etage_1 = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="Rez-de-chaussée"
        )

        self.etage_2 = Etage.objects.create(
            batiment=self.batiment,
            numero=2,
            nom="Premier étage"
        )

        # Plans
        self.plan_1 = Plan.objects.create(
            etage=self.etage_1,
            largeur=1000,
            hauteur=800
        )

        self.plan_2 = Plan.objects.create(
            etage=self.etage_2,
            largeur=1000,
            hauteur=800
        )

        # Salles
        self.salle_1 = Salle.objects.create(
            etage=self.etage_1,
            nom="Salle 101"
        )

        self.salle_2 = Salle.objects.create(
            etage=self.etage_2,
            nom="Salle 201"
        )

        # Équipement
        self.equipement = Equipement.objects.create(
            nom="PC-001",
            numero_inventaire="INV-001",
            situation="AFFECTE"
        )

    def test_localiser_equipement(self):
        """
        Un équipement affecté peut être localisé
        sur un plan correspondant à sa salle.
        """

        position = LocalisationService.localiser_equipement(
            equipement=self.equipement,
            salle=self.salle_1,
            plan=self.plan_1,
            x=200,
            y=300
        )

        self.assertEqual(position.equipement, self.equipement)
        self.assertEqual(position.plan, self.plan_1)
        self.assertEqual(position.x, 200)
        self.assertEqual(position.y, 300)

        self.equipement.refresh_from_db()

        self.assertEqual(
            self.equipement.salle,
            self.salle_1
        )

    def test_equipement_en_stock_ne_peut_pas_etre_localise(self):
        """
        Un équipement en stock ne peut pas être placé
        sur un plan.
        """

        self.equipement.situation = "EN_STOCK"
        self.equipement.save()

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_1,
                x=200,
                y=300
            )

    def test_salle_et_plan_doivent_etre_sur_le_meme_etage(self):
        """
        Une salle et un plan appartenant à des étages différents
        ne peuvent pas être associés.
        """

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_2,
                x=200,
                y=300
            )

    def test_coordonnees_negatives_interdites(self):
        """
        Les coordonnées négatives sont interdites.
        """

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_1,
                x=-10,
                y=300
            )

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_1,
                x=200,
                y=-10
            )

    def test_coordonnees_hors_plan_interdites(self):
        """
        Les coordonnées doivent rester dans les dimensions
        du plan.
        """

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_1,
                x=1001,
                y=300
            )

        with self.assertRaises(ValueError):
            LocalisationService.localiser_equipement(
                equipement=self.equipement,
                salle=self.salle_1,
                plan=self.plan_1,
                x=200,
                y=801
            )

    def test_deplacer_equipement(self):
        """
        Un équipement déjà localisé peut être déplacé.
        """

        LocalisationService.localiser_equipement(
            equipement=self.equipement,
            salle=self.salle_1,
            plan=self.plan_1,
            x=200,
            y=300
        )

        position = LocalisationService.deplacer_equipement(
            equipement=self.equipement,
            plan=self.plan_1,
            x=500,
            y=600
        )

        self.assertEqual(position.x, 500)
        self.assertEqual(position.y, 600)

        self.assertEqual(
            Position.objects.filter(
                equipement=self.equipement
            ).count(),
            1
        )

    def test_deplacement_vers_un_autre_etage_interdit(self):
        """
        Un équipement d'une salle d'un étage ne peut pas être
        déplacé vers un plan d'un autre étage.
        """

        LocalisationService.localiser_equipement(
            equipement=self.equipement,
            salle=self.salle_1,
            plan=self.plan_1,
            x=200,
            y=300
        )

        with self.assertRaises(ValueError):
            LocalisationService.deplacer_equipement(
                equipement=self.equipement,
                plan=self.plan_2,
                x=500,
                y=600
            )

    def test_deplacement_equipement_non_localise_interdit(self):
        """
        Un équipement qui n'a aucune position ne peut pas
        être déplacé.
        """

        with self.assertRaises(ValueError):
            LocalisationService.deplacer_equipement(
                equipement=self.equipement,
                plan=self.plan_1,
                x=500,
                y=600
            )

    def test_retirer_localisation(self):
        """
        La localisation d'un équipement peut être supprimée.
        """

        LocalisationService.localiser_equipement(
            equipement=self.equipement,
            salle=self.salle_1,
            plan=self.plan_1,
            x=200,
            y=300
        )

        LocalisationService.retirer_localisation(
            self.equipement
        )

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )


class PositionnementAutomatiqueTest(TestCase):
    """
    Le positionnement automatique declenche par l'attribution
    d'une salle (EquipementSerializer.create / update).
    """

    def setUp(self):
        self.batiment = Batiment.objects.create(
            nom="Bâtiment A"
        )

        self.etage_1 = Etage.objects.create(
            batiment=self.batiment,
            numero=1,
            nom="Rez-de-chaussée"
        )

        self.etage_2 = Etage.objects.create(
            batiment=self.batiment,
            numero=2,
            nom="Premier étage"
        )

        # Le plan de l'etage 1 declare ses dimensions,
        # celui de l'etage 2 non.
        self.plan_1 = Plan.objects.create(
            etage=self.etage_1,
            largeur=1000,
            hauteur=800
        )

        self.plan_2 = Plan.objects.create(
            etage=self.etage_2
        )

        self.salle_1 = Salle.objects.create(
            etage=self.etage_1,
            nom="Salle 101"
        )

        self.salle_2 = Salle.objects.create(
            etage=self.etage_2,
            nom="Salle 201"
        )

        self.equipement = Equipement.objects.create(
            nom="PC-001",
            numero_inventaire="INV-001",
            situation="AFFECTE"
        )

    def test_une_salle_attribuee_positionne_au_centre(self):
        """
        Attribuer une salle cree une Position au centre du plan.
        """

        self.equipement.salle = self.salle_1
        self.equipement.save()

        position = LocalisationService.positionner_si_affecte(
            self.equipement
        )

        self.assertIsNotNone(position)
        self.assertEqual(position.plan, self.plan_1)
        self.assertEqual(position.x, 500)
        self.assertEqual(position.y, 400)

    def test_sans_dimensions_le_centre_reprend_les_defauts(self):
        """
        Un plan sans dimensions utilise le canevas par defaut
        du visualiseur (1000 x 700).
        """

        self.equipement.salle = self.salle_2
        self.equipement.save()

        position = LocalisationService.positionner_si_affecte(
            self.equipement
        )

        self.assertEqual(position.plan, self.plan_2)
        self.assertEqual(position.x, 500)
        self.assertEqual(position.y, 350)

    def test_l_emplacement_choisi_est_conserve(self):
        """
        Le positionnement automatique n'ecrase jamais
        une position saisie par un administrateur.
        """

        LocalisationService.localiser_equipement(
            equipement=self.equipement,
            salle=self.salle_1,
            plan=self.plan_1,
            x=123,
            y=456
        )

        position = LocalisationService.positionner_si_affecte(
            self.equipement
        )

        self.assertEqual(position.x, 123)
        self.assertEqual(position.y, 456)

    def test_un_changement_de_salle_deplace_le_marqueur(self):
        """
        Changer d'etage deplace le materiel sur le plan
        de l'etage de destination.
        """

        self.equipement.salle = self.salle_1
        self.equipement.save()

        LocalisationService.positionner_si_affecte(self.equipement)

        self.equipement.salle = self.salle_2
        self.equipement.save()

        position = LocalisationService.positionner_si_affecte(
            self.equipement
        )

        self.assertEqual(position.plan, self.plan_2)

    def test_un_materiel_en_stock_ne_reste_pas_sur_le_plan(self):
        """
        Transfere vers le stock, le materiel perd sa position.
        """

        self.equipement.salle = self.salle_1
        self.equipement.save()

        LocalisationService.positionner_si_affecte(self.equipement)

        self.equipement.situation = "EN_STOCK"
        self.equipement.condition_stock = "NEUF"
        self.equipement.salle = None
        self.equipement.save()

        resultat = LocalisationService.positionner_si_affecte(
            self.equipement
        )

        self.assertIsNone(resultat)
        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )

    def test_sans_plan_sur_l_etage_aucune_position(self):
        """
        Un etage dépourvu de plan ne cree aucune position.
        """

        Salle.objects.create(
            etage=Etage.objects.create(
                batiment=self.batiment,
                numero=3,
                nom="Deuxième étage"
            ),
            nom="Salle 301"
        )

        salle_sans_plan = Salle.objects.get(nom="Salle 301")

        self.equipement.salle = salle_sans_plan
        self.equipement.save()

        self.assertIsNone(
            LocalisationService.positionner_si_affecte(
                self.equipement
            )
        )

        self.assertFalse(
            Position.objects.filter(
                equipement=self.equipement
            ).exists()
        )