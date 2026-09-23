<template>
    <div class="utilisateurs-page">

        <div class="page-header">
            <div>
                <h1>Utilisateurs</h1>
                <p>Gestion des comptes et des rôles.</p>
            </div>

            <button
                v-if="estAdmin"
                class="btn-primary"
                @click="ouvrirCreation"
            >
                + Nouvel utilisateur
            </button>
        </div>


        <!-- Message d'erreur -->

        <div v-if="erreur" class="message erreur">
            {{ erreur }}
        </div>


        <!-- Chargement -->

        <div v-if="chargement" class="message">
            Chargement des utilisateurs...
        </div>


        <!-- Liste -->

        <div v-else class="table-container">

            <table>

                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nom d'utilisateur</th>
                        <th>Email</th>
                        <th>Rôle</th>

                        <th v-if="estAdmin">
                            Actions
                        </th>
                    </tr>
                </thead>

                <tbody>

                    <tr
                        v-for="utilisateur in utilisateurs"
                        :key="utilisateur.id"
                    >

                        <td>
                            {{ utilisateur.id }}
                        </td>

                        <td>
                            {{ utilisateur.username }}
                        </td>

                        <td>
                            {{ utilisateur.email || "-" }}
                        </td>

                        <td>

                            <span
                                class="role"
                                :class="{
                                    admin:
                                        utilisateur.role === 'ADMIN',

                                    user:
                                        utilisateur.role === 'USER'
                                }"
                            >
                                {{ utilisateur.role }}
                            </span>

                        </td>

                        <td v-if="estAdmin">

                            <button
                                class="btn-edit"
                                @click="ouvrirModification(utilisateur)"
                            >
                                Modifier
                            </button>

                            <button
                                class="btn-delete"
                                @click="supprimer(utilisateur)"
                            >
                                Supprimer
                            </button>

                        </td>

                    </tr>

                </tbody>

            </table>

        </div>


        <!-- FORMULAIRE -->

        <div
            v-if="formulaireVisible"
            class="modal-overlay"
            @click.self="fermerFormulaire"
        >

            <div class="modal">

                <h2>
                    {{
                        modeModification
                            ? "Modifier l'utilisateur"
                            : "Créer un utilisateur"
                    }}
                </h2>


                <form @submit.prevent="enregistrer">

                    <div class="form-group">

                        <label>
                            Nom d'utilisateur
                        </label>

                        <input
                            v-model="formulaire.username"
                            type="text"
                            required
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Email
                        </label>

                        <input
                            v-model="formulaire.email"
                            type="email"
                        >

                    </div>


                    <div class="form-group">

                        <label>
                            Rôle
                        </label>

                        <select
                            v-model="formulaire.role"
                        >
                            <option value="USER">
                                Utilisateur
                            </option>

                            <option value="ADMIN">
                                Administrateur
                            </option>
                        </select>

                    </div>


                    <div class="form-group">

                        <label>
                            Mot de passe
                        </label>

                        <input
                            v-model="formulaire.password"
                            type="password"
                            :required="!modeModification"
                            :placeholder="
                                modeModification
                                    ? 'Laisser vide pour conserver le mot de passe'
                                    : ''
                            "
                        >

                    </div>


                    <div class="form-actions">

                        <button
                            type="button"
                            class="btn-cancel"
                            @click="fermerFormulaire"
                        >
                            Annuler
                        </button>

                        <button
                            type="submit"
                            class="btn-primary"
                        >
                            Enregistrer
                        </button>

                    </div>

                </form>

            </div>

        </div>

    </div>
</template>


<script setup>

import { computed, onMounted, ref } from "vue";

import { useAuthStore } from "../stores/auth";

import {
    getUtilisateurs,
    creerUtilisateur,
    modifierUtilisateur,
    supprimerUtilisateur
} from "../services/utilisateurService";


const authStore = useAuthStore();


/*
 * Vérifie que l'utilisateur connecté
 * possède le rôle ADMIN.
 */
const estAdmin = computed(() => {
    return authStore.isAdmin;
});


const utilisateurs = ref([]);

const chargement = ref(false);

const erreur = ref("");

const formulaireVisible = ref(false);

const modeModification = ref(false);

const utilisateurSelectionne = ref(null);


/*
 * Données du formulaire.
 */
const formulaire = ref({
    username: "",
    email: "",
    role: "USER",
    password: "",
});


/*
 * Réinitialise le formulaire.
 */
function reinitialiserFormulaire() {

    formulaire.value = {
        username: "",
        email: "",
        role: "USER",
        password: "",
    };

}


/*
 * Charge les utilisateurs.
 */
async function chargerUtilisateurs() {

    chargement.value = true;

    erreur.value = "";

    try {

        utilisateurs.value =
            await getUtilisateurs();

    } catch (error) {

        console.error(error);

        erreur.value =
            "Impossible de charger les utilisateurs.";

    } finally {

        chargement.value = false;

    }

}


/*
 * Ouvre le formulaire de création.
 */
function ouvrirCreation() {

    modeModification.value = false;

    utilisateurSelectionne.value = null;

    reinitialiserFormulaire();

    formulaireVisible.value = true;

}


/*
 * Ouvre le formulaire de modification.
 */
function ouvrirModification(utilisateur) {

    modeModification.value = true;

    utilisateurSelectionne.value = utilisateur;

    formulaire.value = {
        username: utilisateur.username,
        email: utilisateur.email || "",
        role: utilisateur.role,
        password: "",
    };

    formulaireVisible.value = true;

}


/*
 * Ferme le formulaire.
 */
function fermerFormulaire() {

    formulaireVisible.value = false;

}


/*
 * Enregistre un utilisateur.
 */
async function enregistrer() {

    erreur.value = "";

    try {

        if (modeModification.value) {

            const donnees = {
                username: formulaire.value.username,
                email: formulaire.value.email,
                role: formulaire.value.role,
            };

            /*
             * Le mot de passe n'est envoyé que
             * lorsqu'il a été renseigné.
             */
            if (formulaire.value.password) {

                donnees.password =
                    formulaire.value.password;

            }

            await modifierUtilisateur(
                utilisateurSelectionne.value.id,
                donnees
            );

        } else {

            await creerUtilisateur(
                formulaire.value
            );

        }

        fermerFormulaire();

        await chargerUtilisateurs();

    } catch (error) {

        console.error(error);

        erreur.value =
            "Impossible d'enregistrer l'utilisateur.";

    }

}


/*
 * Supprime un utilisateur.
 */
async function supprimer(utilisateur) {

    /*
     * Évite une suppression accidentelle.
     */
    const confirmation = confirm(
        `Supprimer l'utilisateur "${utilisateur.username}" ?`
    );

    if (!confirmation) {
        return;
    }

    try {

        await supprimerUtilisateur(
            utilisateur.id
        );

        await chargerUtilisateurs();

    } catch (error) {

        console.error(error);

        erreur.value =
            "Impossible de supprimer l'utilisateur.";

    }

}


onMounted(() => {

    chargerUtilisateurs();

});

</script>


<style scoped>

.utilisateurs-page {
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.page-header h1 {
    margin-bottom: 5px;
}

.page-header p {
    margin: 0;
    color: #666;
}

.table-container {
    overflow-x: auto;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    font-weight: 600;
}

.role {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 5px;
    font-size: 12px;
    font-weight: 600;
}

.role.admin {
    background: #eee;
}

.role.user {
    background: #f5f5f5;
}

button {
    padding: 8px 12px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.btn-primary {
    background: #222;
    color: white;
}

.btn-edit {
    margin-right: 8px;
}

.btn-delete {
    color: #b00020;
}

.message {
    padding: 30px;
    text-align: center;
}

.erreur {
    color: #b00020;
}


/* Fenêtre modale */

.modal-overlay {
    position: fixed;
    inset: 0;

    display: flex;
    justify-content: center;
    align-items: center;

    background: rgba(0, 0, 0, 0.4);

    z-index: 1000;
}

.modal {
    width: 450px;
    max-width: 90%;

    padding: 25px;

    background: white;
    border-radius: 10px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 9px;

    border: 1px solid #ccc;
    border-radius: 5px;

    box-sizing: border-box;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;

    margin-top: 20px;
}

.btn-cancel {
    background: #eee;
}

</style>