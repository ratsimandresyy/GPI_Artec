<template>
    <div class="page-container etages-page">

        <!--
            Contexte hiérarchique. Il reste affiché pendant le
            chargement pour que l'administrateur sache immédiatement
            dans quel bâtiment il se trouve.
        -->

        <HierarchyContext :niveaux="hierarchie" />

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Étages
                </h1>

                <p class="page-heading__subtitle">
                    <template v-if="batiment">
                        {{ batiment.nom }}
                    </template>

                    <template v-else>
                        Bâtiment
                    </template>
                </p>
            </div>

            <div class="page-heading__actions">
                <router-link
                    v-if="batiment"
                    :to="`/batiments/${batiment.id}/etages`"
                    class="btn-ghost btn-sm"
                >
                    Bâtiment
                </router-link>

                <button
                    v-if="estAdmin"
                    type="button"
                    class="btn-primary"
                    @click="ouvrirFormulaire"
                >
                    Ajouter un étage
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
            titre="Chargement des étages…"
        />

        <!-- Liste -->

        <template v-else-if="etages.length > 0">
            <p class="resultats-compte">
                <span class="resultats-compte__valeur">
                    {{ etages.length }}
                </span>
                étage{{ etages.length > 1 ? 's' : '' }}
            </p>

            <ul class="grille-cartes liste-cartes">
                <li
                    v-for="etage in etages"
                    :key="etage.id"
                >
                    <article class="carte">
                        <div class="carte__entete">
                            <h2 class="carte__titre">
                                {{ libelleNom(etage) }}
                            </h2>

                            <span class="carte__meta">
                                Étage n°{{ etage.numero }}
                            </span>
                        </div>

                        <p class="carte__description">
                            Un étage regroupe des salles.
                        </p>

                        <div class="carte__actions">
                            <!--
                                Libellé explicite : la destination est
                                le contenu de cet étage, pas
                                l'étage lui-même déjà affiché.
                            -->
                            <router-link
                                :to="`/etages/${etage.id}/salles`"
                                class="btn-secondary btn-sm"
                            >
                                Voir les salles
                            </router-link>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-edit btn-sm"
                                @click="modifier(etage)"
                            >
                                Modifier
                            </button>

                            <button
                                v-if="estAdmin"
                                type="button"
                                class="btn-delete btn-sm"
                                @click="demanderSuppression(etage)"
                            >
                                Supprimer
                            </button>
                        </div>
                    </article>
                </li>
            </ul>
        </template>

        <!-- Aucun étage -->

        <EmptyState
            v-else-if="!errorMessage"
            titre="Aucun étage enregistré"
            :message="`Ce bâtiment ne comporte encore aucun étage. Ajoutez-en un pour pouvoir y déclarer des salles.`"
        >
            <button
                v-if="estAdmin"
                type="button"
                class="btn-primary btn-sm"
                @click="ouvrirFormulaire"
            >
                Ajouter le premier étage
            </button>
        </EmptyState>

        <!-- Formulaire -->

        <section
            v-if="formulaireVisible"
            class="formulaire"
            aria-labelledby="titre-formulaire-etage"
        >
            <h2
                id="titre-formulaire-etage"
                class="formulaire__titre"
            >
                {{ modeEdition ? "Modifier l'étage" : "Ajouter un étage" }}
            </h2>

            <p class="formulaire__legende">
                <template v-if="batiment">
                    L'étage sera rattaché au bâtiment
                    <strong>{{ batiment.nom }}</strong>.
                </template>

                Les champs marqués d'un astérisque sont obligatoires.
            </p>

            <form @submit.prevent="enregistrer">
                <div class="formulaire__groupe">
                    <p class="formulaire__groupe-titre">
                        Identification
                    </p>

                    <div class="form-group">
                        <label for="etage-numero">
                            Numéro
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <input
                            id="etage-numero"
                            v-model="formulaire.numero"
                            type="number"
                            required
                            :aria-invalid="Boolean(erreurChamp('numero'))"
                            :class="{
                                'champ-obligatoire': erreurChamp('numero'),
                            }"
                            :aria-describedby="erreurChamp('numero') ? 'etage-numero-erreur' : undefined"
                        >

                        <p
                            v-if="erreurChamp('numero')"
                            id="etage-numero-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurChamp("numero") }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="etage-nom">
                            Nom
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <input
                            id="etage-nom"
                            v-model="formulaire.nom"
                            type="text"
                            required
                            :aria-invalid="Boolean(erreurChamp('nom'))"
                            :class="{
                                'champ-obligatoire': erreurChamp('nom'),
                            }"
                            :aria-describedby="erreurChamp('nom') ? 'etage-nom-erreur' : undefined"
                            placeholder="Ex : Premier étage"
                        >

                        <p
                            v-if="erreurChamp('nom')"
                            id="etage-nom-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurChamp("nom") }}
                        </p>
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
            v-if="etageASupprimer"
            titre="Supprimer cet étage ?"
            :message="`L'étage « ${libelleNom(etageASupprimer)} » sera définitivement supprimé.`"
            consequence="Ses salles seront également supprimées, ainsi que le plan associé s'il en existe un. Cette action est irréversible."
            @confirm="supprimer"
            @cancel="etageASupprimer = null"
        />

    </div>
</template>

<script setup>
/**
 * Gestion des étages d'un bâtiment.
 *
 * La page affiche en permanence le bâtiment courant : un étage sans
 * son contexte n'a pas de sens. Le fil de hiérarchie fournit ce
 * contexte et permet de remonter d'un cran.
 *
 * La liste des étages est filtrée côté page à partir de l'API des
 * étages : ce comportement existant est conservé tel quel.
 */
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import {
    getEtages,
    creerEtage,
    modifierEtage,
    supprimerEtage,
} from "../services/etageService";

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

// État
const etages = ref([]);
const batiment = ref(null);

const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const erreursChamps = ref({});

// Formulaire
const formulaireVisible = ref(false);
const modeEdition = ref(false);
const etageASupprimer = ref(null);

const formulaire = ref({
    numero: "",
    nom: "",
});

const etageEnCours = ref(null);

const FORMULAIRE_VIDE = { numero: "", nom: "" };

// Vérification du rôle
const estAdmin = computed(() => {
    return authStore.isAdmin;
});

const batimentId = computed(() => route.params.batimentId);

/*
 * Fil de hiérarchie Bâtiments → Étages. Le dernier niveau est la page
 * courante : il n'est donc pas un lien.
 */
const hierarchie = computed(() => [
    {
        cle: 'batiments',
        libelle: 'Bâtiments',
        lien: '/batiments',
    },
    {
        cle: 'batiment',
        libelle: batiment.value?.nom || 'Bâtiment',
        lien: batiment.value
            ? `/batiments/${batiment.value.id}/etages`
            : null,
    },
    {
        cle: 'etages',
        libelle: 'Étages',
    },
]);

/*
 * Le modèle autorise un nom vide : l'affichage retombait alors sur
 * une chaîne vide, illisible dans une carte.
 */
function libelleNom(etage) {
    return etage.nom || `Étage n°${etage.numero}`;
}

function erreurChamp(champ) {
    return erreursChamps.value[champ] || "";
}

/**
 * Extrait les erreurs renvoyées par l'API.
 *
 * L'API reste l'autorité de la validation : ses messages sont
 * affichés tels quels plutôt que remplacés.
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
        batiment.value = await getBatiment(batimentId.value);

        const tousLesEtages = await getEtages();

        // On garde uniquement les étages
        // appartenant au bâtiment sélectionné.
        etages.value = tousLesEtages.filter(
            (etage) => String(etage.batiment) === String(batimentId.value)
        );

    } catch (error) {
        console.error(error);

        errorMessage.value = "Impossible de charger les étages.";

    } finally {
        loading.value = false;
    }
}

// Ouvrir le formulaire
function ouvrirFormulaire() {
    modeEdition.value = false;

    formulaire.value = { ...FORMULAIRE_VIDE };
    erreursChamps.value = {};

    etageEnCours.value = null;

    formulaireVisible.value = true;
}

// Modifier
function modifier(etage) {
    modeEdition.value = true;

    etageEnCours.value = etage;

    formulaire.value = {
        numero: etage.numero,
        nom: etage.nom,
    };

    erreursChamps.value = {};

    formulaireVisible.value = true;
}

// Fermer
function fermerFormulaire() {
    formulaireVisible.value = false;
    etageEnCours.value = null;
    erreursChamps.value = {};
}

// Enregistrer
async function enregistrer() {
    saving.value = true;
    errorMessage.value = "";
    erreursChamps.value = {};

    try {
        const donnees = {
            batiment: batimentId.value,
            numero: formulaire.value.numero,
            nom: formulaire.value.nom,
        };

        if (modeEdition.value) {
            await modifierEtage(etageEnCours.value.id, donnees);
            notificationStore.success("Étage modifié avec succès");

        } else {
            await creerEtage(donnees);
            notificationStore.success("Étage créé avec succès");
        }

        fermerFormulaire();

        await chargerDonnees();

    } catch (error) {
        console.error(error);

        erreursChamps.value = extraireErreurs(error);

        errorMessage.value =
            erreursChamps.value.detail ||
            "Impossible d'enregistrer l'étage.";

        notificationStore.error(errorMessage.value);

    } finally {
        saving.value = false;
    }
}

// Demander la confirmation avant suppression
function demanderSuppression(etage) {
    etageASupprimer.value = etage;
}

// Supprimer
async function supprimer() {
    const etage = etageASupprimer.value;

    if (!etage) {
        return;
    }

    try {
        await supprimerEtage(etage.id);

        etageASupprimer.value = null;
        notificationStore.success("Étage supprimé avec succès");
        await chargerDonnees();

    } catch (error) {
        console.error(error);

        etageASupprimer.value = null;

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de supprimer l'étage.";

        notificationStore.error(errorMessage.value);
    }
}

onMounted(() => {
    chargerDonnees();
});
</script>

<style scoped>
.etages-page {
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
