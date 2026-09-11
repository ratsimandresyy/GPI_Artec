<template>
    <div class="login-container">
        <div class="login-card">

            <h1>GPI</h1>
            <h2>Connexion</h2>

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

async function seConnecter() {
    errorMessage.value = "";

    try {
        await authStore.seConnecter(
            username.value,
            password.value
        );

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
</style>