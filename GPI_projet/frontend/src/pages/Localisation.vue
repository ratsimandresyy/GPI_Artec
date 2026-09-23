<template>

    <div class="page">

        <div class="page-header">

            <div>
                <h1>Localisation des équipements</h1>

                <p>
                    Visualisation des équipements sur le plan
                    du bâtiment.
                </p>
            </div>

        </div>


        <!-- Sélection du bâtiment et de l'étage -->

        <div class="selection-panel">

            <div class="form-group">

                <label for="batiment">
                    Bâtiment
                </label>

                <select
                    id="batiment"
                    v-model="batimentSelectionne"
                    @change="changerBatiment"
                >

                    <option value="">
                        Sélectionner un bâtiment
                    </option>

                    <option
                        v-for="batiment in batiments"
                        :key="batiment.id"
                        :value="batiment.id"
                    >
                        {{ batiment.nom }}
                    </option>

                </select>

            </div>


            <div class="form-group">

                <label for="etage">
                    Étage
                </label>

                <select
                    id="etage"
                    v-model="etageSelectionne"
                    @change="chargerPlan"
                    :disabled="!batimentSelectionne"
                >

                    <option value="">
                        Sélectionner un étage
                    </option>

                    <option
                        v-for="etage in etagesFiltres"
                        :key="etage.id"
                        :value="etage.id"
                    >
                        {{ etage.nom }}
                    </option>

                </select>

            </div>

        </div>


        <!-- Chargement -->

        <p v-if="loading">
            Chargement du plan...
        </p>


        <!-- Erreur -->

        <p
            v-if="errorMessage"
            class="error"
        >
            {{ errorMessage }}
        </p>


        <!-- Plan -->

        <div
            v-if="plan"
            class="plan-section"
        >

            <div class="plan-header">

                <h2>
                    Plan :
                    {{ etageCourant?.nom }}
                </h2>

                <span>
                    {{ positions.length }}
                    équipement(s) localisé(s)
                </span>

            </div>


            <PlanViewer
                :plan="plan"
                :positions="positions"
                :est-admin="estAdmin"
            />

        </div>


        <!-- Aucun plan -->

        <div
            v-if="
                etageSelectionne &&
                !loading &&
                !plan
            "
            class="empty"
        >

            Aucun plan n'est disponible pour
            cet étage.

        </div>

    </div>

</template>


<script setup>

import {
    ref,
    computed,
    onMounted,
} from "vue";

import {
    getBatiments,
} from "../services/batimentService";

import {
    getEtages,
} from "../services/etageService";

import {
    getPlans,
    getPositionsParPlan,
} from "../services/localisationService";

import PlanViewer from "../components/PlanViewer.vue";

import { useAuthStore } from "../stores/auth.js";


// Données

const batiments = ref([]);
const etages = ref([]);
const plans = ref([]);
const positions = ref([]);

const plan = ref(null);

const authStore = useAuthStore();
const estAdmin = computed(() => authStore.isAdmin);


// Sélections

const batimentSelectionne = ref("");
const etageSelectionne = ref("");


// État

const loading = ref(false);
const errorMessage = ref("");


// Étages du bâtiment sélectionné

const etagesFiltres = computed(() => {

    if (!batimentSelectionne.value) {
        return [];
    }

    return etages.value.filter(
        (etage) =>
            String(etage.batiment) ===
            String(batimentSelectionne.value)
    );

});


// Étage courant

const etageCourant = computed(() => {

    return etages.value.find(
        (etage) =>
            String(etage.id) ===
            String(etageSelectionne.value)
    );

});


// Charger les données initiales

async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const [
            donneesBatiments,
            donneesEtages,
            donneesPlans,
        ] = await Promise.all([
            getBatiments(),
            getEtages(),
            getPlans(),
        ]);

        batiments.value = donneesBatiments;
        etages.value = donneesEtages;
        plans.value = donneesPlans;

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les données.";

    } finally {

        loading.value = false;

    }

}


// Changer de bâtiment

function changerBatiment() {

    // On réinitialise l'étage
    etageSelectionne.value = "";

    // On supprime le plan affiché
    plan.value = null;

    // On supprime les positions
    positions.value = [];

}


// Charger le plan de l'étage

async function chargerPlan() {

    if (!etageSelectionne.value) {

        plan.value = null;
        positions.value = [];

        return;

    }


    loading.value = true;
    errorMessage.value = "";

    try {

        // Chercher le plan correspondant
        // à l'étage sélectionné.

        plan.value = plans.value.find(
            (p) =>
                String(p.etage) ===
                String(etageSelectionne.value)
        );


        if (!plan.value) {

            positions.value = [];

            return;

        }


        // Récupérer les positions
        // associées au plan.

        positions.value =
            await getPositionsParPlan(
                plan.value.id
            );

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger le plan.";

    } finally {

        loading.value = false;

    }

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
    margin-bottom: 25px;
}


.page-header h1 {
    margin-bottom: 5px;
}


.page-header p {
    margin: 0;
    color: #666;
}


.selection-panel {
    display: flex;
    gap: 20px;

    padding: 20px;

    margin-bottom: 25px;

    border: 1px solid #ddd;
    border-radius: 10px;

    background: white;
}


.form-group {
    display: flex;
    flex-direction: column;

    min-width: 250px;
}


.form-group label {
    margin-bottom: 6px;
    font-weight: 600;
}


.form-group select {
    padding: 10px;

    border: 1px solid #ccc;
    border-radius: 6px;

    background: white;
}


.plan-section {
    margin-top: 20px;
}


.plan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-bottom: 15px;
}


.plan-header h2 {
    margin: 0;
}


.plan-header span {
    color: #666;
}


.error {
    color: #b00020;
}


.empty {
    padding: 40px;

    text-align: center;

    color: #666;

    border: 1px solid #ddd;
    border-radius: 10px;
}


@media (max-width: 700px) {

    .selection-panel {
        flex-direction: column;
    }

    .form-group {
        width: 100%;
    }

}

</style>