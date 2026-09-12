import { defineStore } from "pinia";
import { login } from "../services/authService";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        // Récupération des informations sauvegardées
        // lors du chargement de l'application.
        accessToken: localStorage.getItem("accessToken"),
        refreshToken: localStorage.getItem("refreshToken"),

        user: JSON.parse(
            localStorage.getItem("user") || "null"
        ),
    }),

    getters: {
        isAuthenticated: (state) => {
            return state.accessToken !== null;
        },

        isAdmin: (state) => {
            return state.user?.role === "ADMIN";
        },
    },

    actions: {
        async seConnecter(username, password) {
            const data = await login(username, password);

            // Stockage des tokens
            this.accessToken = data.access;
            this.refreshToken = data.refresh;

            // Récupération de l'utilisateur connecté
            this.user = data.user;

            // Sauvegarde dans localStorage
            localStorage.setItem(
                "accessToken",
                data.access
            );

            localStorage.setItem(
                "refreshToken",
                data.refresh
            );

            localStorage.setItem(
                "user",
                JSON.stringify(data.user)
            );
        },

        seDeconnecter() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;

            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
            localStorage.removeItem("user");
        },
    },
});