<template>
    <div class="login-container">
        <div class="login-card">

            <div class="login-header">
                <button @click="retourDashboard" class="back-button">
                    ← Retour
                </button>
            </div>

            <h1>GPI</h1>
            <h2>Connexion Administrateur</h2>

            <form @submit.prevent="seConnecter">
                <div class="form-group">
                    <label for="username">
                        Nom d'utilisateur
                    </label>
                    <input id="username" v-model="username" type="text" required />
                </div>

                <div class="form-group">
                    <label for="password">
                        Mot de passe
                    </label>
                    <input id="password" v-model="password" type="password" required />
                </div>

                <button type="submit">
                    Se Connecter
                </button>
            </form>

            <p v-if="errorMessage" class="error">
                {{  errorMessage  }}
            </p>

            <div class="visitor-info">
                <h3>Visiteur ?</h3>
                <p>
                    Vous n'avez pas besoin de compte pour accéder aux fonctionnalités visiteur.
                </p>
                <router-link to="/plan" class="visitor-link">
                    → Voir le plan du système
                </router-link>
                <br>
                <router-link to="/signaler" class="visitor-link">
                    → Signaler un problème
                </router-link>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from "vue-router";
import { useAuthStore } from '../stores/auth';

const username = ref("");
const password = ref("");
const errorMessage = ref("");

const router = useRouter();
const authStore = useAuthStore();

function retourDashboard() {
    router.push('/dashboard-public');
}

async function seConnecter() {
    errorMessage.value = "";

    try {
        await authStore.seConnecter(
            username.value,
            password.value
        );

        // Vérifier que l'utilisateur a le rôle ADMIN
        if (authStore.user?.role !== "ADMIN") {
            errorMessage.value = "Accès refusé. Seuls les administrateurs peuvent se connecter.";
            authStore.seDeconnecter();
            return;
        }

        router.push("/dashboard");
    } catch (error) {
        console.error(error);

        errorMessage.value = "Nom d'utilisateur ou mot de passe incorrect.";
    }
}
</script> 

<style scoped>
.login-container {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
}

.login-card {
    width: 350px;
    padding: 30px;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.login-header {
    margin-bottom: 20px;
}

.back-button {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    font-size: 14px;
    padding: 0;
}

.back-button:hover {
    color: #333;
}

.form-group {
    margin-bottom: 15px;
}

label {
    display: block;
    margin-bottom: 5px;
}

input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
}

button {
    width: 100%;
    padding: 10px;
    cursor: pointer;
}

.error {
    margin-top: 15px;
}

.visitor-info {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ddd;
}

.visitor-info h3 {
    margin: 0 0 10px 0;
    font-size: 16px;
}

.visitor-info p {
    margin: 5px 0;
    color: #666;
}

.visitor-link {
    display: inline-block;
    margin-top: 10px;
    color: #2563eb;
    text-decoration: none;
    font-weight: 600;
}

.visitor-link:hover {
    text-decoration: underline;
}
</style>