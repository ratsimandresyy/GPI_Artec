<template>
    <div class="page-container salles-page">

        <!--
            Contexte hiérarchique Bâtiments → Étages → Salles, affiché
            en permanence.
        -->

        <HierarchyContext :niveaux="hierarchie" />

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Salles
                </h1>

                <p class="page-heading__subtitle">
                    <template v-if="etage">
                        {{ libelleNom(etage) }}
                    </template>

                    <template v-else>
                        Étage
                    </template>
                </p>
            </div>

            <div class="page-heading__actions">
                <router-link
                    v-if="etage"
                    :to="`/etages/${etage.id}/salles`"
                    class="btn-ghost btn-sm"
                >
                    Étage
                </router-link>

                <button
                    v-if="estAdmin"
                    type="button"
                    class="btn-primary"
                    @click="ouvrirFormulaire"
                >
                    Ajouter une salle
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
            titre="Chargement des salles…"
        />

        <!-- Liste -->

        <template v-else-if="salles.length > 0">
            <p class="resultats-compte">
                <span class="resultats-compte__valeur">
                    {{ salles.length }}
                </span>
                salle{{ salles.length > 1 ? 's' : '' }}
            </p>

            <ul class="grille-cartes liste-cartes">
                <li
                    v-for="salle in salles"
                    :key="salle.id"
                >
                    <article class="carte">
                        <div class="carte__entete">
                            <h2 class="carte__titre">
                                {{ salle.nom }}
                            </h2>

                            <span class="carte__meta">
                                #{{ salle.id }}
                            </span>
                        </div>

                        <p class="carte__description">
                            {{ salle.description || "Aucune description." }}
                        </p>

                        <div class="carte__actions">
                            <!--
                                Dernier niveau de la hiérarchie : la
                                salle mène à ses équipements.
                            -->
                            <router-link
                                :to="`/salles/${salle.id}/equipements`"
                                class="btn-secondary btn-sm"
                            >
                                Voir les équipements
                            </router-link>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-edit btn-sm"
                                @click="modifier(salle)"
                            >
                                Modifier
                            </button>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-delete btn-sm"
                                @click="demanderSuppression(salle)"
                            >
                                Supprimer
                            </button>
                        </div>
                    </article>
                </li>
            </ul>
        </template>

        <!-- Aucune salle -->

        <EmptyState
            v-else-if="!errorMessage"
            titre="Aucune salle enregistrée"
            :message="`Cet étage ne comporte encore aucune salle. Ajoutez-en une pour y affecter des équipements.`"
        >
            <button
                v-if="estAdmin"
                type="button"
                class="btn-primary btn-sm"
                @click="ouvrirFormulaire"
            >
                Ajouter la première salle
            </button>
        </EmptyState>

        <!-- Formulaire -->

        <section
            v-if="formulaireVisible"
            class="formulaire"
            aria-labelledby="titre-formulaire-salle"
        >
            <h2
                id="titre-formulaire-salle"
                class="formulaire__titre"
            >
                {{ modeEdition ? "Modifier la salle" : "Ajouter une salle" }}
            </h2>

            <p class="formulaire__legende">
                <template v-if="etage">
                    La salle sera rattachée à
                    <strong>{{ libelleNom(etage) }}</strong>.
                </template>

                Les champs marqués d'un astérisque sont obligatoires.
            </p>

            <form @submit.prevent="enregistrer">
                <div class="formulaire__groupe">
                    <p class="formulaire__groupe-titre">
                        Identification
                    </p>

                    <div class="form-group">
                        <label for="salle-nom">
                            Nom
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <input
                            id="salle-nom"
                            v-model="formulaire.nom"
                            type="text"
                            required
                            :aria-invalid="Boolean(erreurChamp('nom'))"
                            :class="{
                                'champ-obligatoire': erreurChamp('nom'),
                            }"
                            aria-describedby="salle-nom-erreur"
                            placeholder="Ex : Salle 101"
                        >

                        <p
                            v-if="erreurChamp('nom')"
                            id="salle-nom-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurChamp("nom") }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="salle-description">
                            Description
                        </label>

                        <textarea
                            id="salle-description"
                            v-model="formulaire.description"
                            rows="4"
                            placeholder="Description de la salle…"
                        ></textarea>
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
        </section>

        <!-- Confirmation de suppression -->

        <ConfirmDialog
            v-if="salleASupprimer"
            titre="Supprimer cette salle ?"
            :message="`La salle « ${salleASupprimer.nom} » sera définitivement supprimée.`"
            consequence="Cette action est irréversible."
            @confirm="supprimer"
            @cancel="salleASupprimer = null"
        />

    </div>
</template>

<script setup>
/**
 * Gestion des salles d'un étage.
 *
 * Le bâtiment est résolu pour que le contexte complet
 * Bâtiment → Étage → Salle reste visible : la salle est le dernier
 * niveau de la hiérarchie du parc, elle n'a pas de sens seule.
 *
 * Le filtrage des salles par étage et l'ensemble des écritures
 * passent par le service : le comportement existant est conservé.
 */
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import {
    getSalles,
    creerSalle,
    modifierSalle,
    supprimerSalle,
} from "../services/salleService";

import { getEtage } from "../services/etageService";
import { getBatiment } from "../services/batimentService";

import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";

import AppAlert from "../components/AppAlert.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import EmptyState from "../components/EmptyState.vue";
import HierarchyContext from "../components/HierarchyContext.vue";
import LoadingState from "../components/LoadingState.vue";

const route = useRoute();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

// Données
const salles = ref([]);
const etage = ref(null);
const batiment = ref(null);

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const erreursChamps = ref({});

// Formulaire
const formulaireVisible = ref(false);
const modeEdition = ref(false);
const salleASupprimer = ref(null);

const salleEnCours = ref(null);

const formulaire = ref({
    nom: "",
    description: "",
});

const FORMULAIRE_VIDE = { nom: "", description: "" };

// Vérification du rôle
const estAdmin = computed(() => {
    return authStore.isAdmin;
});

const etageId = computed(() => route.params.etageId);

/*
 * Le modèle autorise un nom d'étage vide : l'affichage retombait
 * alors sur une chaîne vide.
 */
function libelleNom(etage) {
    if (!etage) {
        return "Étage";
    }

    return etage.nom || `Étage n°${etage.numero}`;
}

/*
 * Fil de hiérarchie. Le bâtiment est résolu via l'identifiant porté
 * par l'étage : c'est la seule information dont la page dispose.
 */
const hierarchie = computed(() => [
    {
        cle: 'batiments',
        libelle: 'Bâtiments',
        lien: '/batiments',
    },
    {
        cle: 'batiment',
        libelle: batiment.value?.nom,
        lien: batiment.value
            ? `/batiments/${batiment.value.id}/etages`
            : null,
    },
    {
        cle: 'etage',
        libelle: etage.value ? libelleNom(etage.value) : 'Étage',
        lien: etage.value
            ? `/etages/${etage.value.id}/salles`
            : null,
    },
    {
        cle: 'salles',
        libelle: 'Salles',
    },
]);

function erreurChamp(champ) {
    return erreursChamps.value[champ] || "";
}

/**
 * Extrait les erreurs renvoyées par l'API, sans les réécrire.
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

// Charger les données
async function chargerDonnees() {
    loading.value = true;
    errorMessage.value = "";

    try {
        // Récupérer l'étage courant
        etage.value = await getEtage(etageId.value);

        /*
         * Le bâtiment n'est pas nécessaire pour charger la page : si
         * cet appel échoue, on conserve les salles et on affiche
         * simplement un libellé générique dans le fil.
         */
        if (etage.value?.batiment) {
            try {
                batiment.value = await getBatiment(etage.value.batiment);

            } catch (erreurBatiment) {
                console.error(
                    "Erreur lors du chargement du bâtiment :",
                    erreurBatiment
                );
            }
        }

        // Récupérer toutes les salles
        const toutesLesSalles = await getSalles();

        // Garder uniquement les salles
        // appartenant à l'étage sélectionné.
        salles.value = toutesLesSalles.filter(
            (salle) =>
                String(salle.etage) === String(etageId.value)
        );

    } catch (error) {
        console.error(error);

        errorMessage.value = "Impossible de charger les salles.";

    } finally {
        loading.value = false;
    }
}

// Ouvrir le formulaire
function ouvrirFormulaire() {
    modeEdition.value = false;

    salleEnCours.value = null;

    formulaire.value = { ...FORMULAIRE_VIDE };
    erreursChamps.value = {};

    formulaireVisible.value = true;
}

// Modifier
function modifier(salle) {
    modeEdition.value = true;

    salleEnCours.value = salle;

    formulaire.value = {
        nom: salle.nom,
        description: salle.description || "",
    };

    erreursChamps.value = {};

    formulaireVisible.value = true;
}

// Fermer le formulaire
function fermerFormulaire() {
    formulaireVisible.value = false;
    salleEnCours.value = null;
    erreursChamps.value = {};
}

// Enregistrer
async function enregistrer() {
    saving.value = true;
    errorMessage.value = "";
    erreursChamps.value = {};

    try {
        const donnees = {
            etage: etageId.value,
            nom: formulaire.value.nom,
            description: formulaire.value.description,
        };

        if (modeEdition.value) {
            await modifierSalle(salleEnCours.value.id, donnees);
            notificationStore.success("Salle modifiée avec succès");

        } else {
            await creerSalle(donnees);
            notificationStore.success("Salle créée avec succès");
        }

        fermerFormulaire();

        await chargerDonnees();

    } catch (error) {
        console.error(error);

        erreursChamps.value = extraireErreurs(error);

        errorMessage.value =
            erreursChamps.value.detail ||
            "Impossible d'enregistrer la salle.";

        notificationStore.error(errorMessage.value);

    } finally {
        saving.value = false;
    }
}

// Demander la confirmation avant suppression
function demanderSuppression(salle) {
    salleASupprimer.value = salle;
}

// Supprimer
async function supprimer() {
    const salle = salleASupprimer.value;

    if (!salle) {
        return;
    }

    try {
        await supprimerSalle(salle.id);

        salleASupprimer.value = null;
        notificationStore.success("Salle supprimée avec succès");
        await chargerDonnees();

    } catch (error) {
        console.error(error);

        salleASupprimer.value = null;

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de supprimer la salle.";

        notificationStore.error(errorMessage.value);
    }
}

onMounted(() => {
    chargerDonnees();
});
</script>

<style scoped>
.salles-page {
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
