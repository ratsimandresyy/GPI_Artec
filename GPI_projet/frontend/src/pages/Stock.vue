<template>

    <div class="page">

        <!-- En-tête -->

        <div class="page-header">

            <div>
                <h1>Gestion du stock</h1>

                <p>
                    Gestion des équipements actuellement en stock.
                </p>
            </div>

        </div>


        <!-- Chargement -->

        <p
            v-if="loading"
            class="info"
        >
            Chargement du stock...
        </p>


        <!-- Erreur -->

        <p
            v-if="errorMessage"
            class="error"
        >
            {{ errorMessage }}
        </p>


        <!-- Résumé -->

        <div
            v-if="!loading"
            class="summary"
        >

            <div class="summary-card">

                <span class="summary-label">
                    Équipements en stock
                </span>

                <strong>
                    {{ equipementsStock.length }}
                </strong>

            </div>


            <div class="summary-card">

                <span class="summary-label">
                    En maintenance
                </span>

                <strong>
                    {{ nombreEnMaintenance }}
                </strong>

            </div>


            <div class="summary-card">

                <span class="summary-label">
                    Prêts à être affectés
                </span>

                <strong>
                    {{ nombrePrets }}
                </strong>

            </div>

        </div>


        <!-- Aucun équipement -->

        <div
            v-if="
                !loading &&
                equipementsStock.length === 0
            "
            class="empty"
        >

            Aucun équipement n'est actuellement en stock.

        </div>


        <!-- Liste du stock -->

        <div
            v-if="equipementsStock.length > 0"
            class="stock-container"
        >

            <div
                v-for="equipement in equipementsStock"
                :key="equipement.id"
                class="stock-card"
            >

                <!-- Informations -->

                <div class="equipment-info">

                    <h2>
                        {{ equipement.nom }}
                    </h2>

                    <p>
                        <strong>
                            N° inventaire :
                        </strong>

                        {{ equipement.numero_inventaire }}
                    </p>

                    <p>
                        <strong>
                            Type :
                        </strong>

                        {{ equipement.type_equipement }}
                    </p>

                    <p>
                        <strong>
                            Condition :
                        </strong>

                        {{ afficherCondition(
                            equipement.condition_stock
                        ) }}
                    </p>

                </div>


                <!-- État -->

                <div class="equipment-status">

                    <span
                        class="status"
                        :class="classeEtat(equipement.etat)"
                    >
                        {{ afficherEtat(equipement.etat) }}
                    </span>

                </div>


                <!-- Actions -->

                <div class="equipment-actions">

                    <!-- Terminer maintenance -->

                    <button
                        v-if="
                            equipement.etat ===
                            'EN_MAINTENANCE'
                        "
                        class="button secondary"
                        :disabled="
                            actionEnCours ===
                            equipement.id
                        "
                        @click="
                            terminerMaintenanceEquipement(
                                equipement
                            )
                        "
                    >

                        {{
                            actionEnCours === equipement.id
                                ? "Traitement..."
                                : "Terminer la maintenance"
                        }}

                    </button>

                    <p class="info-affectation">
                        Pour affecter un équipement, utilisez le drag & drop sur le plan graphique.
                    </p>

                </div>

            </div>

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
    getEquipementsDashboard,
} from "../services/dashboardService";

import {
    terminerMaintenance,
} from "../services/stockService";


// --------------------------------------------------
// Données
// --------------------------------------------------

const equipements = ref([]);


// --------------------------------------------------
// État de la page
// --------------------------------------------------

const loading = ref(false);
const errorMessage = ref("");

const actionEnCours = ref(null);


// --------------------------------------------------
// Équipements en stock
// --------------------------------------------------

const equipementsStock = computed(() => {

    return equipements.value.filter(
        (equipement) =>
            equipement.situation === "EN_STOCK"
    );

});


// --------------------------------------------------
// Statistiques
// --------------------------------------------------

const nombreEnMaintenance = computed(() => {

    return equipementsStock.value.filter(
        (equipement) =>
            equipement.etat === "EN_MAINTENANCE"
    ).length;

});

const nombrePrets = computed(() => {

    return equipementsStock.value.filter(
        (equipement) =>
            equipement.etat === "EN_SERVICE"
    ).length;

});


// --------------------------------------------------
// Chargement initial
// --------------------------------------------------

async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        equipements.value = await getEquipementsDashboard();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les données du stock.";

    } finally {

        loading.value = false;

    }

}


// --------------------------------------------------
// Terminer la maintenance
// --------------------------------------------------

async function terminerMaintenanceEquipement(
    equipement
) {

    actionEnCours.value = equipement.id;
    errorMessage.value = "";

    try {
        await terminerMaintenance(equipement.id);

        // Recharger les données
        await chargerDonnees();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de terminer la maintenance.";

    } finally {

        actionEnCours.value = null;

    }

}


// --------------------------------------------------
// Affichage conditionnel
// --------------------------------------------------

function afficherCondition(condition) {

    if (!condition) return "-";

    const conditions = {
        "NEUF": "Neuf",
        "OCCASION": "Occasion",
        "RECONDITIONNE": "Reconditionné",
    };

    return conditions[condition] || condition;

}


function afficherEtat(etat) {

    const etats = {
        "EN_SERVICE": "En service",
        "EN_MAINTENANCE": "En maintenance",
        "EN_PANNE": "En panne",
        "HORS_SERVICE": "Hors service",
    };

    return etats[etat] || etat;

}


function classeEtat(etat) {

    return `status-${etat.toLowerCase()}`;

}


onMounted(() => {
    chargerDonnees();
});

</script>


<style scoped>

.page {
    padding: 30px;
}


.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    margin: 0 0 5px 0;
}

.page-header p {
    margin: 0;
    color: #666;
}


.summary {
    display: grid;

    grid-template-columns: repeat(3, 1fr);

    gap: 20px;

    margin-bottom: 30px;
}


.summary-card {
    padding: 20px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 10px;

    text-align: center;
}


.summary-label {
    display: block;

    margin-bottom: 10px;

    color: #666;

    font-size: 14px;
}


.summary-card strong {
    font-size: 28px;

    color: #333;
}


.stock-container {
    display: grid;

    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));

    gap: 20px;
}


.stock-card {
    padding: 20px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 10px;

    display: grid;

    grid-template-columns: 1fr auto;

    gap: 20px;

    align-items: center;
}


.equipment-info h2 {
    margin: 0 0 10px 0;
    font-size: 18px;
}


.equipment-info p {
    margin: 5px 0;
    font-size: 14px;
}


.equipment-status {
    text-align: center;
}


.status {
    display: inline-block;

    padding: 7px 12px;

    border-radius: 20px;

    font-size: 13px;

    font-weight: 600;
}


.status-maintenance {
    background: #fff3cd;

    color: #856404;
}


.status-service {
    background: #d4edda;

    color: #155724;
}


.status-hors-service {
    background: #f8d7da;

    color: #721c24;
}


.equipment-actions {
    display: flex;

    flex-direction: column;

    gap: 10px;
}

.info-affectation {
    font-size: 12px;
    color: #666;
    font-style: italic;
    margin-top: 10px;
}


.button {
    border: none;

    border-radius: 6px;

    padding: 10px 15px;

    cursor: pointer;

    font-weight: 600;
}


.button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}


.button.primary {
    background: #333;
    color: white;
}


.button.secondary {
    background: #eee;
    color: #333;
}


.info {
    color: #666;
}


.error {
    margin-bottom: 15px;
    color: #b00020;
}


.empty {
    padding: 50px;
    text-align: center;
    color: #666;
    background: white;
    border: 1px solid #ddd;
    border-radius: 10px;
}


@media (max-width: 900px) {

    .summary {
        grid-template-columns:
            1fr;
    }

    .stock-card {
        grid-template-columns:
            1fr;
    }

    .equipment-status {
        text-align: left;
    }

}

</style>
