<template>
    <main class="login-container">

        <div class="login-card">

            <div class="login-header">
                <!--
                    `type="button"` explicite : sans lui, ce bouton
                    serait interprété comme un bouton d'envoi.
                -->
                <button
                    type="button"
                    class="back-button"
                    @click="retourDashboard"
                >
                    <span aria-hidden="true">←</span>
                    Retour
                </button>
            </div>

            <h1 class="login-titre">
                GPI
            </h1>

            <h2 class="login-sous-titre">
                Connexion Administrateur
            </h2>

            <form
                class="login-formulaire"
                novalidate
                @submit.prevent="seConnecter"
            >
                <div class="form-group">
                    <!--
                        Pas d'`autofocus` : il vole le focus au titre de
                        la page, qu'un lecteur d'écran doit pouvoir lire
                        avant le formulaire. La tabulation entre ici par
                        le bouton « Retour », puis le champ, ce qui suit
                        l'ordre visuel.
                    -->
                    <label for="username">
                        Nom d'utilisateur
                    </label>

                    <input
                        id="username"
                        v-model="username"
                        type="text"
                        required
                        autocomplete="username"
                        autocapitalize="none"
                        spellcheck="false"
                        :disabled="chargement"
                        :aria-describedby="
                            errorMessage ? 'erreur-connexion' : undefined
                        "
                    >
                </div>

                <div class="form-group">
                    <label for="password">
                        Mot de passe
                    </label>

                    <input
                        id="password"
                        v-model="password"
                        type="password"
                        required
                        autocomplete="current-password"
                        :disabled="chargement"
                        :aria-describedby="
                            errorMessage ? 'erreur-connexion' : undefined
                        "
                    >
                </div>

                <!--
                    L'erreur est placée dans le formulaire et non
                    dessous : elle est ainsi annoncée à sa
                    apparition et décrite par les deux champs via
                    `aria-describedby`.
                -->
                <AppAlert
                    v-if="errorMessage"
                    id="erreur-connexion"
                    class="erreur-connexion"
                    type="error"
                    :message="errorMessage"
                />

                <button
                    type="submit"
                    class="btn-primary login-bouton"
                    :disabled="chargement"
                >
                    {{ chargement ? "Connexion…" : "Se connecter" }}
                </button>
            </form>
        </div>
    </main>
</template>

<script setup>
/**
 * Connexion à l'espace d'administration.
 *
 * Écran réservé à l'administrateur : aucun lien, message ou option
 * destiné au visiteur n'y figure. L'accès public au plan et au
 * signalement reste accessible par la navigation de l'espace public
 * et par ses propres pages ; il n'a pas été retiré de l'application.
 *
 * Points de comportement conservés à l'identique :
 *  - l'ouverture de session passe par `authStore.seConnecter` ;
 *  - un compte dont le rôle n'est pas `ADMIN` est déconnecté
 *    immédiatement et l'accès lui est refusé ;
 *  - aucun rafraîchissement de jeton n'est tenté ici.
 */
import { ref } from "vue";
import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

import AppAlert from "../components/AppAlert.vue";

const username = ref("");
const password = ref("");
const errorMessage = ref("");

// Empêche une seconde soumission pendant la requête.
const chargement = ref(false);

const router = useRouter();
const authStore = useAuthStore();

function retourDashboard() {
    router.push("/dashboard-public");
}

async function seConnecter() {
    if (chargement.value) {
        return;
    }

    errorMessage.value = "";
    chargement.value = true;

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
    } finally {
        chargement.value = false;
    }
}
</script>

<style scoped>
/*
 * `100dvh` tient compte de la barre d'adresse des navigateurs mobiles,
 * qui réduit la hauteur visible ; `100vh` reste en repli.
 */
.login-container {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    min-height: 100dvh;
    padding: 1.5rem 1rem;
    background-color: var(--bg-page);
}

.login-card {
    width: 100%;
    max-width: 380px;
    padding: 1.75rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-md);
}

.login-header {
    margin-bottom: 1.25rem;
}

/*
 * Le bouton de retour est aligné à gauche et n'occupe que la largeur
 * de son texte. Le style global ne s'applique qu'aux `.btn-*`, ce qui
 * évite qu'un bouton secondaire hérite d'une largeur de 100 %.
 */
.back-button {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.25rem 0;
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 0.875rem;
    cursor: pointer;
    transition: color 0.15s ease;
}

.back-button:hover {
    color: var(--text-main);
}

/* Anneau de focus visible au clavier. */
.back-button:focus-visible {
    outline: 2px solid var(--primary);
    outline-offset: 2px;
    border-radius: var(--radius-sm);
}

.login-titre {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    color: var(--primary);
}

.login-sous-titre {
    margin: 0.15rem 0 1.5rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-muted);
}

.login-formulaire {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    margin-bottom: 0;
}

.erreur-connexion {
    margin: 0;
}

.login-bouton {
    width: 100%;
    padding: 0.7rem 1rem;
    font-size: 0.95rem;
    font-weight: 600;
}

@media (max-width: 480px) {
    .login-card {
        padding: 1.25rem;
    }
}
</style>
