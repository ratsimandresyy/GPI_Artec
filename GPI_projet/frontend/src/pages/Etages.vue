<template>
    <div class="page">

        <div class="page-header">
            <div>
                <h1>Étages</h1>
                <p v-if="batiment">
                    Bâtiment : {{ batiment.nom }}
                </p>
            </div>

            <button
                v-if="estAdmin"
                class="btn-primary"
                @click="ouvrirFormulaire"
            >
                + Ajouter un étage
            </button>
        </div>


        <!-- Chargement -->
        <p v-if="loading">
            Chargement des étages...
        </p>


        <!-- Erreur -->
        <p v-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>


        <!-- Liste -->
        <div
            v-if="!loading && etages.length > 0"
            class="etages-grid"
        >

            <div
                v-for="etage in etages"
                :key="etage.id"
                class="etage-card"
            >

                <h2>
                    {{ etage.nom }}
                </h2>

                <p>
                    Étage n°{{ etage.numero }}
                </p>


                <div class="actions">

                    <button
                        class="btn-view"
                        @click="voirEtage(etage.id)"
                    >
                        Voir
                    </button>

                    <template v-if="estAdmin">

                        <button
                            class="btn-edit"
                            @click="modifier(etage)"
                        >
                            Modifier
                        </button>

                        <button
                            class="btn-delete"
                            @click="supprimer(etage)"
                        >
                            Supprimer
                        </button>

                    </template>

                </div>

            </div>

        </div>


        <!-- Aucun étage -->
        <p
            v-if="!loading && etages.length === 0"
            class="empty"
        >
            Aucun étage enregistré pour ce bâtiment.
        </p>


        <!-- Formulaire -->
        <div
            v-if="formulaireVisible"
            class="form-container"
        >

            <h2>
                {{ modeEdition ? "Modifier l'étage" : "Ajouter un étage" }}
            </h2>

            <form @submit.prevent="enregistrer">

                <div class="form-group">

                    <label for="numero">
                        Numéro
                    </label>

                    <input
                        id="numero"
                        v-model="formulaire.numero"
                        type="number"
                        required
                    >

                </div>


                <div class="form-group">

                    <label for="nom">
                        Nom
                    </label>

                    <input
                        id="nom"
                        v-model="formulaire.nom"
                        type="text"
                        required
                    >

                </div>


                <div class="form-actions">

                    <button
                        type="submit"
                        class="btn-primary"
                    >
                        Enregistrer
                    </button>

                    <button
                        type="button"
                        class="btn-secondary"
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
import { useRoute, useRouter } from "vue-router";

import {
    getEtages,
    creerEtage,
    modifierEtage,
    supprimerEtage,
} from "../services/etageService";

import { getBatiment } from "../services/batimentService";

import { useAuthStore } from "../stores/auth";


const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();


// État
const etages = ref([]);
const batiment = ref(null);

const loading = ref(false);
const errorMessage = ref("");


// Formulaire
const formulaireVisible = ref(false);
const modeEdition = ref(false);

const formulaire = ref({
    numero: "",
    nom: "",
});

const etageEnCours = ref(null);


// Vérification du rôle
const estAdmin = computed(() => {
    return authStore.isAdmin;
});


// Charger les données
async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const batimentId = route.params.batimentId;

        batiment.value = await getBatiment(batimentId);

        const tousLesEtages = await getEtages();

        // On garde uniquement les étages
        // appartenant au bâtiment sélectionné.
        etages.value = tousLesEtages.filter(
            (etage) => String(etage.batiment) === String(batimentId)
        );

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les étages.";

    } finally {

        loading.value = false;

    }
}


// Ouvrir le formulaire
function ouvrirFormulaire() {

    modeEdition.value = false;

    formulaire.value = {
        numero: "",
        nom: "",
    };

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

    formulaireVisible.value = true;
}


// Fermer
function fermerFormulaire() {
    formulaireVisible.value = false;
}


// Enregistrer
async function enregistrer() {

    try {

        const donnees = {
            batiment: route.params.batimentId,
            numero: formulaire.value.numero,
            nom: formulaire.value.nom,
        };


        if (modeEdition.value) {

            await modifierEtage(
                etageEnCours.value.id,
                donnees
            );

        } else {

            await creerEtage(donnees);

        }


        fermerFormulaire();

        await chargerDonnees();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible d'enregistrer l'étage.";

    }
}


// Supprimer
async function supprimer(etage) {

    const confirmation = confirm(
        `Voulez-vous supprimer l'étage "${etage.nom}" ?`
    );

    if (!confirmation) {
        return;
    }


    try {

        await supprimerEtage(etage.id);

        await chargerDonnees();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de supprimer l'étage.";

    }
}


// Voir les salles de l'étage
function voirEtage(id) {

    router.push(
        `/etages/${id}/salles`
    );

}


onMounted(() => {
    chargerDonnees();
});

</script>


<style scoped>

.page {
    width: 100%;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.page-header h1 {
    margin-bottom: 5px;
}

.page-header p {
    margin: 0;
    color: #666;
}


.etages-grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fill,
        minmax(250px, 1fr)
    );

    gap: 20px;
}


.etage-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 20px;
    background: white;
}


.etage-card h2 {
    margin-top: 0;
}


.actions {
    display: flex;
    gap: 8px;
    margin-top: 20px;
    flex-wrap: wrap;
}


button {
    border: none;
    border-radius: 6px;
    padding: 9px 14px;
    cursor: pointer;
}


.btn-primary {
    background: #222;
    color: white;
}


.btn-view {
    background: #eee;
}


.btn-edit {
    background: #ddd;
}


.btn-delete {
    background: #f5d5d5;
}


.btn-secondary {
    background: #eee;
}


.form-container {
    margin-top: 30px;
    padding: 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
    max-width: 500px;
}


.form-group {
    margin-bottom: 15px;
}


.form-group label {
    display: block;
    margin-bottom: 5px;
}


.form-group input {
    width: 100%;
    box-sizing: border-box;
    padding: 10px;
}


.form-actions {
    display: flex;
    gap: 10px;
}


.error {
    color: #b00020;
}


.empty {
    color: #666;
}

</style>