<template>
    <div class="page-container utilisateurs-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Utilisateurs
                </h1>

                <p class="page-heading__subtitle">
                    Comptes disposant d'un accès à l'administration.
                </p>
            </div>

            <div class="page-heading__actions">
                <button
                    v-if="estAdmin"
                    type="button"
                    class="btn-primary"
                    @click="ouvrirCreation"
                >
                    Nouvel utilisateur
                </button>
            </div>
        </div>

        <!-- Erreur -->

        <AppAlert
            v-if="erreur"
            type="error"
            :message="erreur"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="chargement"
            titre="Chargement des utilisateurs…"
        />

        <!-- Aucun compte -->

        <EmptyState
            v-else-if="utilisateurs.length === 0"
            titre="Aucun compte"
            message="Aucun compte n'est enregistré sur l'application."
        >
            <button
                v-if="estAdmin"
                type="button"
                class="btn-primary btn-sm"
                @click="ouvrirCreation"
            >
                Créer le premier compte
            </button>
        </EmptyState>

        <!-- Liste -->

        <template v-else>
            <p class="resultats-compte">
                <span class="resultats-compte__valeur">
                    {{ utilisateurs.length }}
                </span>
                compte{{ utilisateurs.length > 1 ? 's' : '' }}
            </p>

            <div class="table-scroll">
                <table>
                    <caption class="visually-hidden">
                        Comptes enregistrés et actions d'administration
                    </caption>

                    <thead>
                        <tr>
                            <th scope="col">Identifiant</th>

                            <th scope="col">
                                Nom d'utilisateur
                            </th>

                            <th scope="col">
                                Adresse e-mail
                            </th>

                            <th scope="col">
                                Rôle
                            </th>

                            <th
                                v-if="estAdmin"
                                scope="col"
                            >
                                Actions
                            </th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr
                            v-for="utilisateur in utilisateurs"
                            :key="utilisateur.id"
                        >
                            <td class="cellule-id">
                                {{ utilisateur.id }}
                            </td>

                            <td>
                                <span class="utilisateur-nom">
                                    {{ utilisateur.username }}
                                </span>
                            </td>

                            <td>
                                <span
                                    v-if="utilisateur.email"
                                    class="cellule-mono"
                                >
                                    {{ utilisateur.email }}
                                </span>

                                <span
                                    v-else
                                    class="text-muted"
                                >
                                    Non renseignée
                                </span>
                            </td>

                            <!--
                                Le rôle est la seule information de
                                statut réellement exposée par l'API :
                                l'API ne renvoie ni is_active ni
                                dernière connexion.
                            -->
                            <td>
                                <span
                                    class="role"
                                    :class="`role-${utilisateur.role.toLowerCase()}`"
                                >
                                    {{ libelleRole(utilisateur.role) }}
                                </span>
                            </td>

                            <td
                                v-if="estAdmin"
                                class="cellule-actions"
                            >
                                <div class="actions-cellule">
                                    <button
                                        type="button"
                                        class="btn-edit btn-sm"
                                        @click="ouvrirModification(utilisateur)"
                                    >
                                        Modifier
                                    </button>

                                    <button
                                        type="button"
                                        class="btn-delete btn-sm"
                                        @click="demanderSuppression(utilisateur)"
                                    >
                                        Supprimer
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </template>

        <!-- Formulaire -->

        <div
            v-if="formulaireVisible"
            class="modal-overlay"
            @click.self="fermerFormulaire"
        >
            <div
                class="modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="titre-formulaire-utilisateur"
            >
                <h2
                    id="titre-formulaire-utilisateur"
                    class="formulaire__titre"
                >
                    {{
                        modeModification
                            ? "Modifier l'utilisateur"
                            : "Créer un utilisateur"
                    }}
                </h2>

                <p class="formulaire__legende">
                    Les champs marqués d'un astérisque sont obligatoires.
                </p>

                <AppAlert
                    v-if="erreur"
                    type="error"
                    :message="erreur"
                />

                <form @submit.prevent="enregistrer">
                    <div class="formulaire__groupe">
                        <p class="formulaire__groupe-titre">
                            Identité
                        </p>

                        <div class="form-group">
                            <label for="utilisateur-username">
                                Nom d'utilisateur
                                <span
                                    class="requis"
                                    aria-hidden="true"
                                >*</span>
                            </label>

                            <input
                                id="utilisateur-username"
                                v-model="formulaire.username"
                                type="text"
                                required
                                :disabled="saving"
                            >
                        </div>

                        <div class="form-group">
                            <label for="utilisateur-email">
                                Adresse e-mail
                            </label>

                            <input
                                id="utilisateur-email"
                                v-model="formulaire.email"
                                type="email"
                                :disabled="saving"
                            >
                        </div>
                    </div>

                    <div class="formulaire__groupe">
                        <p class="formulaire__groupe-titre">
                            Rôle et accès
                        </p>

                        <div class="form-group">
                            <!--
                                En modification, le rôle n'est pas
                                modifiable : l'API le rejette en
                                écriture sur une mise à jour. Il est
                                donc présenté comme une valeur, et
                                non comme un champ, pour ne pas
                                afficher un choix qui serait
                                silencieusement ignoré.
                            -->
                            <label
                                v-if="!modeModification"
                                for="utilisateur-role"
                            >
                                Rôle
                            </label>

                            <p
                                v-else
                                class="champ-etiquette"
                            >
                                Rôle
                            </p>

                            <select
                                v-if="!modeModification"
                                id="utilisateur-role"
                                v-model="formulaire.role"
                                :disabled="saving"
                            >
                                <option value="USER">
                                    Utilisateur
                                </option>

                                <option value="ADMIN">
                                    Administrateur
                                </option>
                            </select>

                            <p
                                v-else
                                class="role role-affichage"
                            >
                                {{ libelleRole(formulaire.role) }}
                            </p>

                            <p class="champ-aide">
                                <template v-if="modeModification">
                                    Le rôle est fixé à la création du
                                    compte et ne peut pas être modifié
                                    ensuite.
                                </template>

                                <template v-else>
                                    Seul un administrateur peut accéder à
                                    l'espace de gestion.
                                </template>
                            </p>
                        </div>

                        <div class="form-group">
                            <label for="utilisateur-password">
                                Mot de passe
                            </label>

                            <input
                                id="utilisateur-password"
                                v-model="formulaire.password"
                                type="password"
                                :required="!modeModification"
                                :disabled="saving"
                                :placeholder="
                                    modeModification
                                        ? 'Laisser vide pour conserver le mot de passe'
                                        : ''
                                "
                            >
                        </div>
                    </div>

                    <div class="formulaire__actions">
                        <button
                            type="button"
                            class="btn-secondary"
                            :disabled="saving"
                            @click="fermerFormulaire"
                        >
                            Annuler
                        </button>

                        <button
                            type="submit"
                            class="btn-primary"
                            :disabled="saving"
                        >
                            {{ saving ? "Enregistrement…" : "Enregistrer" }}
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Confirmation de suppression -->

        <ConfirmDialog
            v-if="utilisateurASupprimer"
            titre="Supprimer ce compte ?"
            :message="`Le compte « ${utilisateurASupprimer.username} » sera définitivement supprimé.`"
            consequence="Cette personne ne pourra plus se connecter à l'administration. Cette action est irréversible."
            @confirm="supprimer"
            @cancel="utilisateurASupprimer = null"
        />

    </div>
</template>

<script setup>
/**
 * Gestion des comptes disposant d'un accès à l'administration.
 *
 * Les seules actions proposées sont celles qui existent déjà côté
 * API : création, modification et suppression. Aucune fonctionnalité
 * n'est ajoutée, en particulier pas d'activation ou de
 * désactivation, l'API n'exposant aucun de ces champs.
 *
 * `estAdmin` ne protège que l'affichage : l'autorisation effective
 * reste vérifiée par Django.
 */
import { computed, onMounted, ref } from "vue";

import { useAuthStore } from "../stores/auth";

import {
    getUtilisateurs,
    creerUtilisateur,
    modifierUtilisateur,
    supprimerUtilisateur
} from "../services/utilisateurService";

import AppAlert from "../components/AppAlert.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import EmptyState from "../components/EmptyState.vue";
import LoadingState from "../components/LoadingState.vue";

const authStore = useAuthStore();

/*
 * Vérifie que l'utilisateur connecté possède le rôle ADMIN.
 */
const estAdmin = computed(() => {
    return authStore.isAdmin;
});

const utilisateurs = ref([]);

const chargement = ref(false);
const saving = ref(false);

const erreur = ref("");

const formulaireVisible = ref(false);

const modeModification = ref(false);

const utilisateurSelectionne = ref(null);
const utilisateurASupprimer = ref(null);

/*
 * Données du formulaire.
 */
const formulaire = ref({
    username: "",
    email: "",
    role: "USER",
    password: "",
});

const FORMULAIRE_VIDE = {
    username: "",
    email: "",
    role: "USER",
    password: "",
};

/*
 * Libellés lisibles des rôles, repris des choix du modèle Django.
 */
const LIBELLES_ROLE = {
    ADMIN: "Administrateur",
    USER: "Utilisateur",
};

function libelleRole(role) {
    return LIBELLES_ROLE[role] || role || "—";
}

/*
 * Réinitialise le formulaire.
 */
function reinitialiserFormulaire() {
    formulaire.value = { ...FORMULAIRE_VIDE };
}

/*
 * Charge les utilisateurs.
 */
async function chargerUtilisateurs() {
    chargement.value = true;

    erreur.value = "";

    try {
        utilisateurs.value = await getUtilisateurs();

    } catch (error) {
        console.error(error);

        erreur.value = "Impossible de charger les utilisateurs.";

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
    utilisateurSelectionne.value = null;
}

/*
 * Enregistre un utilisateur.
 */
async function enregistrer() {
    saving.value = true;
    erreur.value = "";

    try {
        if (modeModification.value) {
            /*
             * `role` n'est volontairement pas transmis : l'API le
             * déclare en lecture seule sur une mise à jour et
             * l'ignorerait. L'envoyer laisserait croire à une
             * modification du rôle qui n'a pas lieu d'être.
             */
            const donnees = {
                username: formulaire.value.username,
                email: formulaire.value.email,
            };

            /*
             * Le mot de passe n'est envoyé que lorsqu'il a été
             * renseigné.
             */
            if (formulaire.value.password) {
                donnees.password = formulaire.value.password;
            }

            await modifierUtilisateur(utilisateurSelectionne.value.id, donnees);

        } else {
            await creerUtilisateur(formulaire.value);
        }

        fermerFormulaire();

        await chargerUtilisateurs();

    } catch (error) {
        console.error(error);

        erreur.value = "Impossible d'enregistrer l'utilisateur.";

    } finally {
        saving.value = false;
    }
}

/*
 * Demande la confirmation avant suppression.
 */
function demanderSuppression(utilisateur) {
    utilisateurASupprimer.value = utilisateur;
}

/*
 * Supprime un utilisateur, après confirmation explicite.
 */
async function supprimer() {
    const utilisateur = utilisateurASupprimer.value;

    if (!utilisateur) {
        return;
    }

    try {
        await supprimerUtilisateur(utilisateur.id);

        utilisateurASupprimer.value = null;
        await chargerUtilisateurs();

    } catch (error) {
        console.error(error);

        utilisateurASupprimer.value = null;

        erreur.value = "Impossible de supprimer l'utilisateur.";
    }
}

onMounted(() => {
    chargerUtilisateurs();
});
</script>

<style scoped>
.utilisateurs-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.cellule-id {
    color: var(--text-light);
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}

.utilisateur-nom {
    font-weight: 600;
    color: var(--text-main);
}

.cellule-mono {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
    color: var(--text-muted);
}

/*
 * Rôle : la forme distingue les deux rôles, pas seulement leur
 * couleur. L'administrateur est plein, l'utilisateur est évidé.
 */
.role {
    display: inline-flex;
    align-items: center;
    padding: 0.3rem 0.6rem;
    border-radius: var(--radius-sm);
    border: 1px solid var(--border-medium);
    font-size: 0.75rem;
    font-weight: 600;
    line-height: 1.2;
    white-space: nowrap;
}

.role-admin {
    background-color: var(--primary);
    color: #ffffff;
    border-color: var(--primary);
}

.role-user {
    background-color: var(--bg-surface);
    color: var(--secondary);
    border-color: var(--border-medium);
    border-style: dashed;
}

/* Rôle en lecture seule dans le formulaire de modification. */
.role-affichage {
    display: flex;
    width: fit-content;
}

/*
 * Étiquette d'une valeur non modifiable : même présentation qu'un
 * label, mais ce n'est pas un `label` puisqu'aucun champ n'est
 * associé.
 */
.champ-etiquette {
    margin-bottom: 0.35rem;
    color: var(--text-main);
    font-size: 0.875rem;
    font-weight: 600;
}

.actions-cellule {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

.cellule-actions {
    white-space: nowrap;
}

.champ-aide {
    margin: 0.35rem 0 0;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

/* Modale */

.modal-overlay {
    z-index: 1000;
    padding: 1.5rem;
}

.modal {
    width: 100%;
    max-width: 520px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 1.5rem;
}

.formulaire__groupe {
    margin: 0 0 1rem;
    padding: 0 0 0.25rem;
    border: none;
    border-bottom: 1px solid var(--border-light);
}

.formulaire__groupe:last-of-type {
    margin-bottom: 0;
    border-bottom: none;
}

@media (max-width: 640px) {
    .actions-cellule {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
