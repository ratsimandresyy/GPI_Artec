<template>
    <div class="profile-page">
        <div class="page-header">
            <div>
                <h1>Mon profil</h1>
                <p>Gestion de mes informations personnelles</p>
            </div>
        </div>

        <!-- Chargement -->
        <p v-if="loading">
            Chargement du profil...
        </p>

        <!-- Erreur -->
        <p v-else-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>

        <!-- Formulaire -->
        <div v-else class="profile-container">
            <div class="profile-card">
                <h2>Informations personnelles</h2>

                <form @submit.prevent="enregistrer">
                    <div class="form-group">
                        <label for="username">Nom d'utilisateur</label>
                        <input
                            id="username"
                            v-model="formulaire.username"
                            type="text"
                            disabled
                        >
                        <small>Le nom d'utilisateur ne peut pas être modifié.</small>
                    </div>

                    <div class="form-group">
                        <label for="email">Email</label>
                        <input
                            id="email"
                            v-model="formulaire.email"
                            type="email"
                            :disabled="enCours"
                        >
                    </div>

                    <div class="form-group">
                        <label for="first_name">Prénom</label>
                        <input
                            id="first_name"
                            v-model="formulaire.first_name"
                            type="text"
                            :disabled="enCours"
                        >
                    </div>

                    <div class="form-group">
                        <label for="last_name">Nom</label>
                        <input
                            id="last_name"
                            v-model="formulaire.last_name"
                            type="text"
                            :disabled="enCours"
                        >
                    </div>

                    <div class="form-group">
                        <label for="role">Rôle</label>
                        <input
                            id="role"
                            v-model="afficherRole"
                            type="text"
                            disabled
                        >
                        <small>Le rôle est géré par l'administrateur.</small>
                    </div>

                    <p v-if="errorMessageFormulaire" class="error">
                        {{ errorMessageFormulaire }}
                    </p>

                    <div class="form-actions">
                        <button
                            type="submit"
                            class="primary-button"
                            :disabled="enCours"
                        >
                            {{ enCours ? 'Enregistrement...' : 'Enregistrer' }}
                        </button>
                    </div>
                </form>
            </div>

            <div class="password-card">
                <h2>Changer le mot de passe</h2>

                <form @submit.prevent="changerMotDePasse">
                    <div class="form-group">
                        <label for="current_password">Mot de passe actuel</label>
                        <input
                            id="current_password"
                            v-model="passwordForm.current_password"
                            type="password"
                            :disabled="passwordEnCours"
                        >
                    </div>

                    <div class="form-group">
                        <label for="new_password">Nouveau mot de passe</label>
                        <input
                            id="new_password"
                            v-model="passwordForm.new_password"
                            type="password"
                            :disabled="passwordEnCours"
                        >
                    </div>

                    <div class="form-group">
                        <label for="confirm_password">Confirmer le mot de passe</label>
                        <input
                            id="confirm_password"
                            v-model="passwordForm.confirm_password"
                            type="password"
                            :disabled="passwordEnCours"
                        >
                    </div>

                    <p v-if="errorMessagePassword" class="error">
                        {{ errorMessagePassword }}
                    </p>

                    <p v-if="succesPassword" class="success">
                        Mot de passe modifié avec succès.
                    </p>

                    <div class="form-actions">
                        <button
                            type="submit"
                            class="primary-button"
                            :disabled="passwordEnCours"
                        >
                            {{ passwordEnCours ? 'Modification...' : 'Changer le mot de passe' }}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getMonProfil, modifierMonProfil } from '../services/utilisateurService';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const loading = ref(false);
const errorMessage = ref('');

const formulaire = ref({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    role: ''
});

const passwordForm = ref({
    current_password: '',
    new_password: '',
    confirm_password: ''
});

const enCours = ref(false);
const passwordEnCours = ref(false);
const errorMessageFormulaire = ref('');
const errorMessagePassword = ref('');
const succesPassword = ref(false);

const afficherRole = computed(() => {
    const roleMap = {
        'ADMIN': 'Administrateur',
        'USER': 'Utilisateur'
    };
    return roleMap[formulaire.value.role] || formulaire.value.role;
});

async function chargerProfil() {
    loading.value = true;
    errorMessage.value = '';

    try {
        const profil = await getMonProfil();
        formulaire.value = {
            username: profil.username,
            email: profil.email || '',
            first_name: profil.first_name || '',
            last_name: profil.last_name || '',
            role: profil.role
        };
    } catch (error) {
        console.error('Erreur lors du chargement du profil:', error);
        errorMessage.value = 'Impossible de charger le profil.';
    } finally {
        loading.value = false;
    }
}

async function enregistrer() {
    enCours.value = true;
    errorMessageFormulaire.value = '';

    try {
        await modifierMonProfil({
            email: formulaire.value.email,
            first_name: formulaire.value.first_name,
            last_name: formulaire.value.last_name
        });

        /*
         * La mise à jour de la session passe par le store : il reste
         * le seul point d'écriture de l'état de connexion.
         */
        authStore.mettreAJourUtilisateur({
            email: formulaire.value.email,
            first_name: formulaire.value.first_name,
            last_name: formulaire.value.last_name
        });

        errorMessageFormulaire.value = '';
    } catch (error) {
        console.error('Erreur lors de la modification:', error);
        errorMessageFormulaire.value = error.response?.data?.detail || 'Impossible de modifier le profil.';
    } finally {
        enCours.value = false;
    }
}

async function changerMotDePasse() {
    errorMessagePassword.value = '';
    succesPassword.value = false;

    if (!passwordForm.value.current_password) {
        errorMessagePassword.value = 'Veuillez saisir le mot de passe actuel.';
        return;
    }

    if (!passwordForm.value.new_password) {
        errorMessagePassword.value = 'Veuillez saisir le nouveau mot de passe.';
        return;
    }

    if (passwordForm.value.new_password.length < 8) {
        errorMessagePassword.value = 'Le mot de passe doit contenir au moins 8 caractères.';
        return;
    }

    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
        errorMessagePassword.value = 'Les mots de passe ne correspondent pas.';
        return;
    }

    passwordEnCours.value = true;

    try {
        // Note: Pour l'instant, Django ne gère pas le changement de mot de passe via l'API
        // Cette fonctionnalité nécessiterait une modification backend supplémentaire
        errorMessagePassword.value = 'Cette fonctionnalité nécessite une configuration backend supplémentaire.';
    } catch (error) {
        console.error('Erreur lors du changement de mot de passe:', error);
        errorMessagePassword.value = error.response?.data?.detail || 'Impossible de changer le mot de passe.';
    } finally {
        passwordEnCours.value = false;
    }
}

onMounted(() => {
    chargerProfil();
});
</script>

<style scoped>
.profile-page {
    padding: 30px;
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    margin: 0;
    font-size: 28px;
}

.page-header p {
    margin: 5px 0 0;
    color: var(--text-muted);
}

.profile-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 20px;
}

.profile-card,
.password-card {
    padding: 25px;
    background: white;
    border: 1px solid var(--border-light);
    border-radius: 10px;
}

.profile-card h2,
.password-card h2 {
    margin-top: 0;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
}

.form-group input {
    width: 100%;
    padding: 10px;
    border: 1px solid var(--border-medium);
    border-radius: 6px;
    box-sizing: border-box;
}

.form-group small {
    display: block;
    margin-top: 5px;
    color: var(--text-muted);
    font-size: 12px;
}

.form-actions {
    margin-top: 20px;
}

.primary-button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background: var(--primary);
    color: var(--on-primary);
    cursor: pointer;
}

.primary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.error {
    color: var(--danger-text);
    margin-top: 10px;
}

.success {
    color: var(--success-text);
    margin-top: 10px;
}
</style>
