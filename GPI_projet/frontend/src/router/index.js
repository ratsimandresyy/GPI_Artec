import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

import Login from "../pages/Login.vue";
import Dashboard from "../pages/Dashboard.vue";
import DashboardPublic from "../pages/DashboardPublic.vue";
import Equipements from "../pages/Equipements.vue";
import EquipementDetail from "../pages/EquipementDetail.vue";
import MainLayout from "../layouts/MainLayout.vue";
import PublicLayout from "../layouts/PublicLayout.vue";
import AdaptiveLayout from "../layouts/AdaptiveLayout.vue";
import Batiments from "../pages/Batiments.vue";
import Etages from "../pages/Etages.vue";
import Salles from "../pages/Salles.vue";
import EquipementsSalle from "../pages/EquipementsSalle.vue";
import Localisation from "../pages/Localisation.vue";
import PlanPublic from "../pages/PlanPublic.vue";
import Audits from "../pages/Audits.vue";
import Stock from "../pages/Stock.vue";
import Utilisateurs from "../pages/Utilisateurs.vue";
import Tickets from "../pages/Tickets.vue";
import TicketPublic from "../pages/TicketPublic.vue";
import Profile from "../pages/Profile.vue";

const routes = [
    { path: "/", redirect: "/dashboard-public" },

    // Connexion administrateur : accessible, redirigée si déjà connecté.
    { path: "/login", name: "Login", component: Login },

    /*
     * Espace public (mode visiteur).
     * `meta.public` autorise l'accès sans authentification.
     * Seules les fonctionnalités réellement publiques sont déclarées.
     */
    {
        path: "/",
        component: PublicLayout,
        children: [
            {
                path: "dashboard-public",
                name: "DashboardPublic",
                component: DashboardPublic,
                meta: { public: true },
            },
            {
                path: "signaler",
                name: "TicketPublic",
                component: TicketPublic,
                meta: { public: true },
            },
            {
                path: "plan",
                name: "LocalisationPublic",
                component: PlanPublic,
                meta: { public: true },
            },
        ],
    },

    /*
     * Page des équipements : déclarée une seule fois pour éviter deux
     * URLs. Le layout s'adapte (administration pour un admin authentifié,
     * espace public pour un visiteur).
     */
    {
        path: "/equipements",
        component: AdaptiveLayout,
        children: [
            {
                path: "",
                name: "Equipements",
                component: Equipements,
                meta: { public: true },
            },
            {
                path: ":id",
                name: "EquipementDetail",
                component: EquipementDetail,
                meta: { public: true },
            },
        ],
    },

    /*
     * Espace d'administration.
     *
     * `meta.requiresAdmin` est déclaré sur le parent et fusionné par
     * vue-router dans toutes les routes enfants (to.meta). Il s'appuie
     * sur le mécanisme existant : aucune seconde convention n'est
     * introduite.
     */
    {
        path: "/",
        component: MainLayout,
        meta: { requiresAdmin: true },
        children: [
            {
                path: "dashboard",
                name: "Dashboard",
                component: Dashboard,
            },
            {
                path: "batiments",
                name: "Batiments",
                component: Batiments,
            },
            {
                path: "batiments/:batimentId/etages",
                name: "Etages",
                component: Etages,
            },
            {
                path: "etages/:etageId/salles",
                name: "Salles",
                component: Salles,
            },
            {
                path: "salles/:salleId/equipements",
                name: "EquipementsSalle",
                component: EquipementsSalle,
            },
            {
                path: "localisation",
                name: "Localisation",
                component: Localisation,
            },
            {
                // Console de gestion du stock et de la maintenance.
                // Elle complète PlanViewer, qui ne permet pas de terminer
                // une maintenance.
                path: "stock",
                name: "Stock",
                component: Stock,
                meta: { requiresAdmin: true },
            },
            {
                path: "audits",
                name: "Audits",
                component: Audits,
            },
            {
                path: "utilisateurs",
                name: "Utilisateurs",
                component: Utilisateurs,
                meta: { requiresAdmin: true },
            },
            {
                path: "tickets",
                name: "Tickets",
                component: Tickets,
                meta: { requiresAdmin: true },
            },
            {
                path: "profile",
                name: "Profile",
                component: Profile,
                meta: { requiresAdmin: true },
            },
        ],
    },

    // Toute URL inconnue renvoie vers l'espace public.
    { path: "/:pathMatch(.*)*", redirect: "/dashboard-public" },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior: () => ({ top: 0 }),
});

/*
 * Protection des routes.
 *
 * L'état d'authentification et le rôle proviennent du store Pinia,
 * qui est la source de vérité unique. `localStorage` n'est plus
 * interrogé ici.
 *
 * Cette protection organise l'affichage : elle ne remplace en aucun
 * cas les permissions vérifiées par le backend.
 */
router.beforeEach((to) => {
    const authStore = useAuthStore();

    // Un administrateur déjà connecté n'a rien à faire sur /login.
    if (to.name === "Login") {
        if (authStore.isAdmin) {
            return { name: "Dashboard" };
        }

        return true;
    }

    // Espace public : accessible à tous, y compris déconnecté.
    if (to.meta.public) {
        return true;
    }

    /*
     * Tout le reste exige un compte authentifié de rôle ADMIN.
     * Un visiteur ou un compte sans rôle valide est renvoyé vers
     * l'accueil public, qui explique comment se connecter.
     */
    if (to.meta.requiresAdmin) {
        if (!authStore.isAuthenticated || !authStore.isAdmin) {
            return { name: "DashboardPublic" };
        }
    }

    return true;
});

export default router;
