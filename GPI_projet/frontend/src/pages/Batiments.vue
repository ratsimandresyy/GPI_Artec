<template>
    <div class="page-container batiments-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Bâtiments
                </h1>

                <p class="page-heading__subtitle">
                    Un bâtiment regroupe des étages, qui regroupent
                    eux-mêmes des salles.
                </p>
            </div>

            <div class="page-heading__actions">
                <button
                    v-if="estAdmin"
                    type="button"
                    class="btn-primary"
                    @click="ouvrirFormulaireCreation"
                >
                    Ajouter un bâtiment
                </button>
            </div>
        </div>

        <!-- Erreur -->

        <AppAlert
            v-if="errorMessage"
            type="error"
            :message="errorMessage"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="loading"
            titre="Chargement des bâtiments…"
        />

        <!-- Liste -->

        <template v-else-if="batiments.length > 0">
            <p class="resultats-compte">
                <span class="resultats-compte__valeur">
                    {{ batiments.length }}
                </span>
                bâtiment{{ batiments.length > 1 ? 's' : '' }}
            </p>

            <ul class="grille-cartes liste-cartes">
                <li
                    v-for="batiment in batiments"
                    :key="batiment.id"
                >
                    <article class="carte">
                        <div class="carte__entete">
                            <h2 class="carte__titre">
                                {{ batiment.nom }}
                            </h2>

                            <span class="carte__meta">
                                #{{ batiment.id }}
                            </span>
                        </div>

                        <p class="carte__description">
                            {{ batiment.description || "Aucune description." }}
                        </p>

                        <div class="carte__actions">
                            <!--
                                La hiérarchie du parc est linéaire :
                                bâtiment → étages. Le libellé nomme
                                explicitement la destination, plutôt
                                qu'un « Voir » sans objet.
                            -->
                            <router-link
                                :to="`/batiments/${batiment.id}/etages`"
                                class="btn-secondary btn-sm"
                            >
                                Voir les étages
                            </router-link>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-edit btn-sm"
                                @click="ouvrirFormulaireModification(batiment)"
                            >
                                Modifier
                            </button>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-delete btn-sm"
                                @click="demanderSuppression(batiment)"
                            >
                                Supprimer
                            </button>
                        </div>
                    </article>
                </li>
            </ul>
        </template>

        <!-- Aucun bâtiment -->

        <EmptyState
            v-else-if="!errorMessage"
            titre="Aucun bâtiment enregistré"
            message="Le parc ne comporte encore aucun bâtiment. Ajoutez-en un pour commencer à structurer ses étages et ses salles."
        >
            <button
                v-if="estAdmin"
                type="button"
                class="btn-primary btn-sm"
                @click="ouvrirFormulaireCreation"
            >
                Ajouter le premier bâtiment
            </button>
        </EmptyState>

        <!-- Formulaire -->

        <section
            v-if="formulaireVisible"
            class="formulaire"
            aria-labelledby="titre-formulaire-batiment"
        >
            <h2
                id="titre-formulaire-batiment"
                class="formulaire__titre"
            >
                {{
                    modeFormulaire === "creation"
                        ? "Ajouter un bâtiment"
                        : "Modifier le bâtiment"
                }}
            </h2>

            <p class="formulaire__legende">
                Les champs marqués d'un astérisque sont obligatoires.
            </p>

            <form @submit.prevent="enregistrer">
                <div class="form-group">
                    <label for="batiment-nom">
                        Nom du bâtiment
                        <span
                            class="requis"
                            aria-hidden="true"
                        >*</span>
                    </label>

                    <input
                        id="batiment-nom"
                        v-model="formulaire.nom"
                        type="text"
                        required
                        :aria-invalid="Boolean(erreurChamp('nom'))"
                        :class="{
                            'champ-obligatoire': erreurChamp('nom'),
                        }"
                        :aria-describedby="erreurChamp('nom') ? 'batiment-nom-erreur' : undefined"
                        placeholder="Ex : Bâtiment A"
                    >

                    <p
                        v-if="erreurChamp('nom')"
                        id="batiment-nom-erreur"
                        class="champ-erreur"
                    >
                        {{ erreurChamp("nom") }}
                    </p>
                </div>

                <div class="form-group">
                    <label for="batiment-description">
                        Description
                    </label>

                    <textarea
                        id="batiment-description"
                        v-model="formulaire.description"
                        rows="4"
                        placeholder="Description du bâtiment…"
                    ></textarea>
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
        </section>

        <!-- Confirmation de suppression -->

        <ConfirmDialog
            v-if="batimentASupprimer"
            titre="Supprimer ce bâtiment ?"
            :message="`Le bâtiment « ${batimentASupprimer.nom} » sera définitivement supprimé.`"
            consequence="Ses étages et ses salles seront également supprimés. Cette action est irréversible."
            @confirm="supprimer"
            @cancel="batimentASupprimer = null"
        />

    </div>
</template>

<script setup>
/**
 * Gestion des bâtiments.
 *
 * La page ne fait qu'organiser l'affichage : la création, la
 * modification et la suppression passent par le service, et les
 * règles de validation restent celles de l'API.
 *
 * `estAdmin` ne protège que l'affichage : l'autorisation effective
 * reste vérifiée par Django.
 */
import { ref, computed, onMounted } from "vue";

import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";

import {
    getBatiments,
    creerBatiment,
    modifierBatiment,
    supprimerBatiment,
} from "../services/batimentService";

import AppAlert from "../components/AppAlert.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import EmptyState from "../components/EmptyState.vue";
import LoadingState from "../components/LoadingState.vue";

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const batiments = ref([]);

const loading = ref(false);
const saving = ref(false);

const errorMessage = ref("");
const erreursChamps = ref({});

const formulaireVisible = ref(false);

const modeFormulaire = ref("creation");

const batimentSelectionne = ref(null);
const batimentASupprimer = ref(null);

const formulaire = ref({
    nom: "",
    description: "",
});

const FORMULAIRE_VIDE = { nom: "", description: "" };

/*
 * Détermine si l'utilisateur connecté possède le rôle ADMIN.
 *
 * Attention : cette vérification sert uniquement à l'interface.
 * La véritable sécurité reste assurée par Django.
 */
const estAdmin = computed(() => {
    return authStore.isAdmin;
});

function erreurChamp(champ) {
    return erreursChamps.value[champ] || "";
}

/**
 * Charge la liste des bâtiments.
 */
async function chargerBatiments() {
    loading.value = true;
    errorMessage.value = "";

    try {
        batiments.value = await getBatiments();

    } catch (error) {
        console.error(
            "Erreur lors du chargement des bâtiments :",
            error
        );

        errorMessage.value = "Impossible de charger les bâtiments.";

    } finally {
        loading.value = false;
    }
}

/**
 * Ouvre le formulaire pour créer un bâtiment.
 */
function ouvrirFormulaireCreation() {
    modeFormulaire.value = "creation";

    batimentSelectionne.value = null;

    formulaire.value = { ...FORMULAIRE_VIDE };
    erreursChamps.value = {};

    formulaireVisible.value = true;
}

/**
 * Ouvre le formulaire pour modifier un bâtiment.
 */
function ouvrirFormulaireModification(batiment) {
    modeFormulaire.value = "modification";

    batimentSelectionne.value = batiment;

    formulaire.value = {
        nom: batiment.nom,
        description: batiment.description || "",
    };

    erreursChamps.value = {};

    formulaireVisible.value = true;
}

/**
 * Ferme le formulaire.
 */
function fermerFormulaire() {
    formulaireVisible.value = false;

    batimentSelectionne.value = null;

    formulaire.value = { ...FORMULAIRE_VIDE };
    erreursChamps.value = {};
}

/**
 * Extrait les erreurs renvoyées par l'API.
 *
 * DRF répond soit par un objet `{ champ: [messages] }`, soit par une
 * liste de messages, soit par `{ detail }`. On ne masque jamais ces
 * messages : le backend reste l'autorité de la validation.
 */
function extraireErreurs(error) {
    const donnees = error.response?.data;

    if (!donnees) {
        return {};
    }

    if (typeof donnees === "string") {
        return { detail: donnees };
    }

    if (Array.isArray(donnees)) {
        return { detail: donnees.join(" ") };
    }

    const champs = {};

    Object.entries(donnees).forEach(([champ, messages]) => {
        champs[champ] = Array.isArray(messages)
            ? messages.join(" ")
            : String(messages);
    });

    return champs;
}

/**
 * Enregistre le bâtiment.
 *
 * Création :
 * POST /inventaire/batiments/
 *
 * Modification :
 * PUT /inventaire/batiments/{id}/
 */
async function enregistrer() {
    saving.value = true;
    errorMessage.value = "";
    erreursChamps.value = {};

    try {
        if (modeFormulaire.value === "creation") {
            await creerBatiment(formulaire.value);
            notificationStore.success("Bâtiment créé avec succès");

        } else {
            await modifierBatiment(
                batimentSelectionne.value.id,
                formulaire.value
            );
            notificationStore.success("Bâtiment modifié avec succès");
        }

        fermerFormulaire();

        await chargerBatiments();

    } catch (error) {
        console.error(
            "Erreur lors de l'enregistrement :",
            error
        );

        erreursChamps.value = extraireErreurs(error);

        errorMessage.value =
            erreursChamps.value.detail ||
            "Impossible d'enregistrer le bâtiment.";

        notificationStore.error(errorMessage.value);

    } finally {
        saving.value = false;
    }
}

/**
 * Demande la confirmation avant de supprimer un bâtiment.
 */
function demanderSuppression(batiment) {
    batimentASupprimer.value = batiment;
}

/**
 * Supprime un bâtiment, après confirmation explicite.
 */
async function supprimer() {
    const batiment = batimentASupprimer.value;

    if (!batiment) {
        return;
    }

    errorMessage.value = "";

    try {
        await supprimerBatiment(batiment.id);

        batimentASupprimer.value = null;
        notificationStore.success("Bâtiment supprimé avec succès");
        await chargerBatiments();

    } catch (error) {
        console.error(
            "Erreur lors de la suppression :",
            error
        );

        batimentASupprimer.value = null;

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de supprimer le bâtiment.";

        notificationStore.error(errorMessage.value);
    }
}

onMounted(() => {
    chargerBatiments();
});
</script>

<style scoped>
.batiments-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* La grille porte sur la <ul> : la carte occupe toute la cellule et
   la liste reste sémantique. */
.liste-cartes {
    margin: 0;
    padding: 0;
    list-style: none;
}

.liste-cartes > li {
    display: flex;
}

.liste-cartes .carte {
    width: 100%;
}
</style>
