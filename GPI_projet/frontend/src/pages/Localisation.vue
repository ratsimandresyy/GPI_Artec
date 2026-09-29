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
                :equipements="equipements"
                :est-admin="estAdmin"
                :equipement-a-mettre-en-evidence="equipementAMettreEnEvidence"
                @position-modifiee="positionModifiee"
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
    getPositions,
    getPositionsParPlan,
} from "../services/localisationService";

import {
    getEquipement,
    getEquipements,
} from "../services/equipementService";

import {
    getSalle,
} from "../services/salleService";

import PlanViewer from "../components/PlanViewer.vue";

import { useRoute } from "vue-router";

import { useAuthStore } from "../stores/auth.js";


const route = useRoute();

// Données

const batiments = ref([]);
const etages = ref([]);
const plans = ref([]);
const positions = ref([]);
const equipements = ref([]);

const plan = ref(null);

const authStore = useAuthStore();
const estAdmin = computed(() => authStore.isAdmin);


// Sélections

const batimentSelectionne = ref("");
const etageSelectionne = ref("");


// État

const loading = ref(false);
const errorMessage = ref("");

/*
 * Équipement à mettre en évidence sur le plan.
 *
 * Renseigné depuis l'URL (?equipementId=) lorsqu'on arrive
 * depuis le bouton « Localiser » de la liste des équipements.
 */
const equipementAMettreEnEvidence = ref(null);


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
            donneesEquipements,
        ] = await Promise.all([
            getBatiments(),
            getEtages(),
            getPlans(),
            getEquipements(),
        ]);

        batiments.value = donneesBatiments;
        etages.value = donneesEtages;
        plans.value = donneesPlans;
        equipements.value = Array.isArray(donneesEquipements)
            ? donneesEquipements
            : (donneesEquipements?.results ?? []);

        // Arrivée depuis le bouton « Localiser » de la liste
        // des équipements : on ouvre directement le bon plan.
        if (route.query.equipementId) {
            await naviguerVersEquipement(
                route.query.equipementId
            );
        }

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les données.";

    } finally {

        loading.value = false;

    }

}


/*
 * Ouvre le plan portant l'équipement passé dans l'URL
 * et le met en évidence.
 */
async function naviguerVersEquipement(equipementId) {

    try {

        const positions = await getPositions();

        const position = positions.find(
            (item) =>
                String(item.equipement) ===
                String(equipementId)
        );

        let planTrouve = null;

        if (position) {

            planTrouve = plans.value.find(
                (item) =>
                    String(item.id) ===
                    String(position.plan)
            );

        } else {

            // L'équipement est affecté à une salle mais n'a
            // pas encore de marqueur : on ouvre le plan de
            // sa salle pour permettre son positionnement.
            const equipement =
                await getEquipement(equipementId);

            if (equipement.salle) {

                const salle = await getSalle(
                    equipement.salle
                );

                planTrouve = plans.value.find(
                    (item) =>
                        String(item.etage) ===
                        String(salle.etage)
                );
            }
        }

        if (!planTrouve) {
            errorMessage.value =
                "Aucun plan disponible pour cet équipement.";
            return;
        }

        const etage = etages.value.find(
            (item) =>
                String(item.id) ===
                String(planTrouve.etage)
        );

        if (etage) {
            batimentSelectionne.value = etage.batiment;
        }

        etageSelectionne.value = planTrouve.etage;

        equipementAMettreEnEvidence.value = equipementId;

        await chargerPlan();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de localiser l'équipement.";

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

function positionModifiee(position) {
    const index = positions.value.findIndex(
        (item) => item.id === position.id
    );

    if (index !== -1) {
        positions.value[index] = position;
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
    color: var(--text-muted);
}


.selection-panel {
    display: flex;
    gap: 20px;

    padding: 20px;

    margin-bottom: 25px;

    border: 1px solid var(--border-light);
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

    border: 1px solid var(--border-medium);
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
    color: var(--text-muted);
}


.error {
    color: var(--danger-text);
}


.empty {
    padding: 40px;

    text-align: center;

    color: var(--text-muted);

    border: 1px solid var(--border-light);
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