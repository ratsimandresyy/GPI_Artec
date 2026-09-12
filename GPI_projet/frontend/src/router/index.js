import { createRouter, createWebHistory } from "vue-router";

import Login from "../pages/Login.vue";
import Dashboard from "../pages/Dashboard.vue";
import Equipements from "../pages/Equipements.vue";
import EquipementDetail from "../pages/EquipementDetail.vue";
import MainLayout from "../layouts/MainLayout.vue";
import Batiments from "../pages/Batiments.vue";
import Etage from "../pages/Etages.vue";
import Salles from "../pages/Salles.vue";
import EquipementsSalle from "../pages/EquipementsSalle.vue";

const routes = [
    { path: "/", redirect: "/dashboard",},
    { path: "/login", name: "Login", component: Login,}, 
    { path: "/", component:MainLayout, meta : {requiresAuth: true,},
        children: [
            { path: "dashboard", name: "Dashboard", component: Dashboard},
            { path: "equipements", name: "Equipements", component: Equipements},
            { path: "equipements/:id", name: "EquipementDetail", component: EquipementDetail},
            { path: "batiments", name: "Batiments", component: Batiments},
            { path: "batiments/:batimentId/etages", name: "Etages", component: Etage},
            { path: "etages/:etageId/salles", name: "Salles", component: Salles},
            { path: "salles/:salleId/equipements", name: "EquipementsSalle", component: EquipementsSalle}
        ]
    }
];

const router = createRouter({ history: createWebHistory(), routes, });

//Protection des pages necessitant une authentification
router.beforeEach((to) => {
    const token = localStorage.getItem("accessToken");

    if (to.meta.requiresAuth && !token) {
        return "/login";
    }

    if (to.path === "/login" && token) {
        return "/dashboard";
    }
});

export default router;