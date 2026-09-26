import { createRouter, createWebHistory } from "vue-router";

import Login from "../pages/Login.vue";
import Dashboard from "../pages/Dashboard.vue";
import DashboardPublic from "../pages/DashboardPublic.vue";
import Equipements from "../pages/Equipements.vue";
import EquipementDetail from "../pages/EquipementDetail.vue";
import MainLayout from "../layouts/MainLayout.vue";
import Batiments from "../pages/Batiments.vue";
import Etage from "../pages/Etages.vue";
import Salles from "../pages/Salles.vue";
import EquipementsSalle from "../pages/EquipementsSalle.vue";
import Localisation from "../pages/Localisation.vue";
import PlanPublic from "../pages/PlanPublic.vue";
import Audits from "../pages/Audits.vue";
import Utilisateurs from "../pages/Utilisateurs.vue";
import Tickets from "../pages/Tickets.vue";
import TicketPublic from "../pages/TicketPublic.vue";
import Profile from "../pages/Profile.vue";

const routes = [
    { path: "/", redirect: "/dashboard-public"},
    { path: "/login", name: "Login", component: Login},
    { path: "/dashboard-public", name: "DashboardPublic", component: DashboardPublic, meta: {public: true}},
    { path: "/signaler", name: "TicketPublic", component: TicketPublic, meta: {public: true}},
    { path: "/plan", name: "LocalisationPublic", component: PlanPublic, meta: {public: true}},
    { path: "/equipements", name: "Equipements", component: Equipements, meta: {public: true}},
    { path: "/equipements/:id", name: "EquipementDetail", component: EquipementDetail, meta: {public: true}},
    { path: "/", component:MainLayout,
        children: [
            { path: "dashboard", name: "Dashboard", component: Dashboard},
            { path: "batiments", name: "Batiments", component: Batiments},
            { path: "batiments/:batimentId/etages", name: "Etages", component: Etage},
            { path: "etages/:etageId/salles", name: "Salles", component: Salles},
            { path: "salles/:salleId/equipements", name: "EquipementsSalle", component: EquipementsSalle},
            { path: "localisation", name: "Localisation", component: Localisation},
            { path: "audits", name: "Audits", component: Audits},
            { path: "utilisateurs", name: "Utilisateurs", component: Utilisateurs, meta: {requiresAdmin: true}},
            { path: "tickets", name: "Tickets", component: Tickets, meta: {requiresAdmin: true}},
            { path: "profile", name: "Profile", component: Profile, meta: {requiresAdmin: true}}
        ]
    }
];

const router = createRouter({ history: createWebHistory(), routes, });

//Protection des pages nécessitant une authentification
router.beforeEach((to) => {
    const token = localStorage.getItem("accessToken");
    const user = JSON.parse(localStorage.getItem("user") || "null");

    // Routes publiques (accessibles sans authentification)
    if (to.meta.public) {
        return;
    }

    // Routes admin uniquement (nécessitent authentification + rôle ADMIN)
    if (to.meta.requiresAdmin) {
        if (!token || user?.role !== "ADMIN") {
            return "/dashboard-public";
        }
    }

    // Routes dans MainLayout (nécessitent authentification)
    if (to.matched.some(record => record.path === "/")) {
        if (!token) {
            return "/dashboard-public";
        }

        // Si l'utilisateur n'est pas ADMIN, rediriger vers le dashboard public
        if (user?.role !== "ADMIN") {
            return "/dashboard-public";
        }
    }

    //Si un administrateur connecté essaie d'aller sur /login
    if (to.path === "/login" && token) {
        return "/dashboard";
    }
});

export default router;