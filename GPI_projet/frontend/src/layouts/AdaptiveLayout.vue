<template>
    <!--
        Layout adaptatif.

        La page Equipements sert deux publics : l'administrateur qui la
        gère, et le visiteur qui la consulte en lecture seule. Elle est
        déclarée une seule fois dans le routeur afin de ne pas créer
        deux URLs pour la même page.

        L'administrateur conserve le shell d'administration, le visiteur
        bascule sur l'espace public.
    -->
    <component
        :is="layoutActif"
    >
        <router-view />
    </component>
</template>

<script setup>
/**
 * Choix du layout selon l'état réel du store d'authentification.
 *
 * Ce composant n'est qu'un point de bascule graphique : il n'autorise
 * rien. Les droits d'accès restent vérifiés par le backend.
 */
import { computed } from "vue";

import { useAuthStore } from "../stores/auth";

import MainLayout from "./MainLayout.vue";
import PublicLayout from "./PublicLayout.vue";

const authStore = useAuthStore();

const layoutActif = computed(() =>
    authStore.isAuthenticated && authStore.isAdmin
        ? MainLayout
        : PublicLayout,
);
</script>
