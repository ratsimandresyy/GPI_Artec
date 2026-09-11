<template>
    <div>
        <h1>Dashboard GPI</h1>

        <p>
            Connexion reussi.
        </p>
        <button @click="seDeconnecter">
            Se deconnecter
        </button>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

import { onMounted } from 'vue';
import api from '../services/api';

const router = useRouter();
const authStore = useAuthStore();

function seDeconnecter() {
    authStore.seDeconecter();
    router.push("/login");
}

onMounted(async () => {
    try {
        const response = await api.get(
            "/inventaire/equipements/"
        );

        console.log("Equipements :", response.data);
    } catch (error) {
        console.error(
            "Erreur lors de la recuperation des equipements :",
            error
        );
    }
});
</script>