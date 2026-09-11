import { createRouter, createWebHistory } from "vue-router";

import Login from "../pages/Login.vue";
import Dashboard from "../pages/Dashboard.vue";
import Equipements from "../pages/Equipements.vue";

const routes = [
    { path: "/", redirect: "/dashboard",},
    { path: "/login", name: "Login", component: Login,},
    { path: "/dashboard", name: "Dashboard", component: Dashboard, meta: { requiresAuth: true,},},
    { path: "/equipements", name: "Equipements", component: Equipements, meta: { requiresAuth: true,},}
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