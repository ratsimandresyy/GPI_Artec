import { defineStore } from "pinia";
import { login } from "../services/authSrevice";

export const useAuthStore = defineStore("auth", {
    state: () => ({
        accessToken: null,
        refreshToken: null,
        user: null,
    }),

    getters: {
        isAuthenticated: (state) => {
            return state.accessToken !== null;
        },
    },

    actions: {
        async seConnecter(username, password) {
            const data = await login(username, password);

            this.accessToken = data.access;
            this.refreshToken = data.refresh;

            localStorage.setItem("accessToken", data.access);
            localStorage.setItem("refreshToken", data.refresh);
        },

        seDeconecter() {
            this.accessToken = null;
            this.refreshToken = null;
            this.user = null;

            localStorage.removeItem("accessToken");
            localStorage.removeItem("refreshToken");
        },
    },
});
