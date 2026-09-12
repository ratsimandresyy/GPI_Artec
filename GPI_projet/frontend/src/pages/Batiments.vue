<template>
    <div class="batiments-page">

        <!-- En-tête -->
        <div class="page-header">
            <div>
                <h1>Bâtiments</h1>
                <p>Gestion des bâtiments du parc informatique</p>
            </div>

            <button
                v-if="estAdmin"
                type="button"
                class="primary-button"
                @click="ouvrirFormulaireCreation"
            >
                + Ajouter un bâtiment
            </button>
        </div>


        <!-- Message d'erreur -->
        <div
            v-if="errorMessage"
            class="message error"
        >
            {{ errorMessage }}
        </div>


        <!-- Chargement -->
        <div
            v-if="loading"
            class="message"
        >
            Chargement des bâtiments...
        </div>


        <!-- Liste -->
        <div
            v-else-if="batiments.length > 0"
            class="batiments-grid"
        >

            <div
                v-for="batiment in batiments"
                :key="batiment.id"
                class="batiment-card"
            >

                <div class="card-header">
                    <h2>{{ batiment.nom }}</h2>

                    <span class="batiment-id">
                        #{{ batiment.id }}
                    </span>
                </div>

                <p class="description">
                    {{ batiment.description || "Aucune description." }}
                </p>

                <div class="card-actions">

                    <button
                        type="button"
                        class="secondary-button"
                        @click="voirBatiment(batiment.id)"
                    >
                        Voir
                    </button>

                    <button
                        v-if="estAdmin"
                        type="button"
                        class="secondary-button"
                        @click="ouvrirFormulaireModification(batiment)"
                    >
                        Modifier
                    </button>

                    <button
                        v-if="estAdmin"
                        type="button"
                        class="danger-button"
                        @click="supprimer(batiment)"
                    >
                        Supprimer
                    </button>

                </div>

            </div>

        </div>


        <!-- Aucun bâtiment -->
        <div
            v-else
            class="empty-message"
        >
            Aucun bâtiment enregistré.
        </div>


        <!-- Formulaire -->
        <div
            v-if="formulaireVisible"
            class="form-container"
        >

            <h2>
                {{
                    modeFormulaire === "creation"
                        ? "Ajouter un bâtiment"
                        : "Modifier le bâtiment"
                }}
            </h2>


            <form @submit.prevent="enregistrer">

                <div class="form-group">
                    <label for="nom">
                        Nom du bâtiment
                    </label>

                    <input
                        id="nom"
                        v-model="formulaire.nom"
                        type="text"
                        required
                        placeholder="Ex : Bâtiment A"
                    />
                </div>


                <div class="form-group">
                    <label for="description">
                        Description
                    </label>

                    <textarea
                        id="description"
                        v-model="formulaire.description"
                        rows="4"
                        placeholder="Description du bâtiment..."
                    ></textarea>
                </div>


                <div class="form-actions">

                    <button
                        type="submit"
                        class="primary-button"
                        :disabled="saving"
                    >
                        {{
                            saving
                                ? "Enregistrement..."
                                : "Enregistrer"
                        }}
                    </button>

                    <button
                        type="button"
                        class="secondary-button"
                        @click="fermerFormulaire"
                    >
                        Annuler
                    </button>

                </div>

            </form>

        </div>

    </div>
</template>


<script setup>

import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";

import {
    getBatiments,
    creerBatiment,
    modifierBatiment,
    supprimerBatiment,
} from "../services/batimentService";


const router = useRouter();
const authStore = useAuthStore();


const batiments = ref([]);

const loading = ref(false);
const saving = ref(false);

const errorMessage = ref("");

const formulaireVisible = ref(false);

const modeFormulaire = ref("creation");

const batimentSelectionne = ref(null);


const formulaire = ref({
    nom: "",
    description: "",
});


/*
 * Détermine si l'utilisateur connecté
 * possède le rôle ADMIN.
 *
 * Attention :
 * cette vérification sert uniquement à l'interface.
 * La véritable sécurité reste assurée par Django.
 */
const estAdmin = computed(() => {
    return authStore.isAdmin;
});

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

        errorMessage.value =
            "Impossible de charger les bâtiments.";

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

    formulaire.value = {
        nom: "",
        description: "",
    };

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

    formulaireVisible.value = true;
}


/**
 * Ferme le formulaire.
 */
function fermerFormulaire() {

    formulaireVisible.value = false;

    batimentSelectionne.value = null;

    formulaire.value = {
        nom: "",
        description: "",
    };
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

    try {

        if (modeFormulaire.value === "creation") {

            await creerBatiment(formulaire.value);

        } else {

            await modifierBatiment(
                batimentSelectionne.value.id,
                formulaire.value
            );
        }

        fermerFormulaire();

        await chargerBatiments();

    } catch (error) {

        console.error(
            "Erreur lors de l'enregistrement :",
            error
        );

        errorMessage.value =
            "Impossible d'enregistrer le bâtiment.";

    } finally {

        saving.value = false;
    }
}


/**
 * Supprime un bâtiment.
 */
async function supprimer(batiment) {

    const confirmation = window.confirm(
        `Voulez-vous vraiment supprimer le bâtiment "${batiment.nom}" ?`
    );

    if (!confirmation) {
        return;
    }

    errorMessage.value = "";

    try {

        await supprimerBatiment(batiment.id);

        await chargerBatiments();

    } catch (error) {

        console.error(
            "Erreur lors de la suppression :",
            error
        );

        errorMessage.value =
            "Impossible de supprimer le bâtiment.";
    }
}


/**
 * Affiche les informations du bâtiment.
 *
 * Pour l'instant, on reste sur la page.
 * La navigation vers les étages sera ajoutée
 * lorsque Etages.vue sera créée.
 */
function voirBatiment(id) {

    console.log(
        "Bâtiment sélectionné :",
        id
    );

    router.push(
        `/batiments/${id}/etages`
    );
}

onMounted(() => {
    chargerBatiments();
});

</script>


<style scoped>

.batiments-page {
    width: 100%;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.page-header h1 {
    margin: 0;
    font-size: 28px;
}

.page-header p {
    margin-top: 6px;
    color: #666;
}


/* Grille des bâtiments */

.batiments-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
}


.batiment-card {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}


.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}


.card-header h2 {
    margin: 0;
    font-size: 20px;
}


.batiment-id {
    color: #777;
    font-size: 13px;
}


.description {
    min-height: 45px;
    margin: 15px 0;
    color: #666;
}


/* Boutons */

.card-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}


.primary-button,
.secondary-button,
.danger-button {
    padding: 9px 14px;
    border-radius: 6px;
    cursor: pointer;
}


.primary-button {
    border: none;
    background: #222;
    color: white;
}


.secondary-button {
    border: 1px solid #ccc;
    background: white;
}


.danger-button {
    border: 1px solid #d9534f;
    background: white;
    color: #d9534f;
}


.primary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}


/* Formulaire */

.form-container {
    margin-top: 30px;
    padding: 25px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}


.form-container h2 {
    margin-top: 0;
}


.form-group {
    margin-bottom: 20px;
}


.form-group label {
    display: block;
    margin-bottom: 7px;
    font-weight: bold;
}


.form-group input,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 5px;
    box-sizing: border-box;
}


.form-actions {
    display: flex;
    gap: 10px;
}


/* Messages */

.message {
    padding: 15px;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 6px;
}


.message.error {
    border-color: #d9534f;
    color: #b52b27;
}


.empty-message {
    padding: 30px;
    text-align: center;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #666;
}


@media (max-width: 1000px) {

    .batiments-grid {
        grid-template-columns: repeat(2, 1fr);
    }

}


@media (max-width: 650px) {

    .page-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 15px;
    }

    .batiments-grid {
        grid-template-columns: 1fr;
    }

}

</style>