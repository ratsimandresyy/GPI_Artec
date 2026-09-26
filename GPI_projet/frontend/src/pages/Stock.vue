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


                    <!-- Affecter -->

                    <button
                        v-if="
                            equipement.etat ===
                            'EN_SERVICE'
                        "
                        class="button primary"
                        @click="
                            ouvrirFormulaireAffectation(
                                equipement
                            )
                        "
                    >

                        Affecter

                    </button>

                </div>

            </div>

        </div>


        <!-- Formulaire d'affectation -->

        <div
            v-if="equipementSelectionne"
            class="modal-overlay"
        >

            <div class="modal">

                <div class="modal-header">

                    <div>

                        <h2>
                            Affecter l'équipement
                        </h2>

                        <p>
                            {{ equipementSelectionne.nom }}
                        </p>

                    </div>

                    <button
                        class="close-button"
                        @click="fermerFormulaireAffectation"
                    >
                        ×
                    </button>

                </div>


                <!-- Bâtiment -->

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


                <!-- Étage -->

                <div class="form-group">

                    <label for="etage">
                        Étage
                    </label>

                    <select
                        id="etage"
                        v-model="etageSelectionne"
                        @change="changerEtage"
                        :disabled="
                            !batimentSelectionne
                        "
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


                <!-- Salle -->

                <div class="form-group">

                    <label for="salle">
                        Salle
                    </label>

                    <select
                        id="salle"
                        v-model="salleSelectionnee"
                        :disabled="
                            !etageSelectionne
                        "
                    >

                        <option value="">
                            Sélectionner une salle
                        </option>

                        <option
                            v-for="salle in sallesFiltrees"
                            :key="salle.id"
                            :value="salle.id"
                        >
                            {{ salle.nom }}
                        </option>

                    </select>

                </div>


                <!-- Plan -->

                <div class="form-group">

                    <label for="plan">
                        Plan
                    </label>

                    <select
                        id="plan"
                        v-model="planSelectionne"
                        :disabled="
                            !etageSelectionne
                        "
                    >

                        <option value="">
                            Sélectionner un plan
                        </option>

                        <option
                            v-for="plan in plansFiltres"
                            :key="plan.id"
                            :value="plan.id"
                        >
                            Plan de {{ nomEtage(plan.etage) }}
                        </option>

                    </select>

                </div>


                <!-- Coordonnées -->

                <div class="coordinates">

                    <div class="form-group">

                        <label for="x">
                            Position X
                        </label>

                        <input
                            id="x"
                            v-model.number="positionX"
                            type="number"
                            min="0"
                        >

                    </div>


                    <div class="form-group">

                        <label for="y">
                            Position Y
                        </label>

                        <input
                            id="y"
                            v-model.number="positionY"
                            type="number"
                            min="0"
                        >

                    </div>

                </div>


                <!-- Erreur du formulaire -->

                <p
                    v-if="formError"
                    class="error"
                >
                    {{ formError }}
                </p>


                <!-- Actions du formulaire -->

                <div class="modal-actions">

                    <button
                        class="button secondary"
                        @click="
                            fermerFormulaireAffectation
                        "
                    >
                        Annuler
                    </button>

                    <button
                        class="button primary"
                        :disabled="affectationEnCours"
                        @click="affecter"
                    >

                        {{
                            affectationEnCours
                                ? "Affectation..."
                                : "Affecter l'équipement"
                        }}

                    </button>

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
    affecterEquipement,
} from "../services/stockService";

import {
    getBatiments,
} from "../services/batimentService";

import {
    getEtages,
} from "../services/etageService";

import {
    getSalles,
} from "../services/salleService";

import {
    getPlans,
} from "../services/localisationService";


// --------------------------------------------------
// Données
// --------------------------------------------------

const equipements = ref([]);

const batiments = ref([]);
const etages = ref([]);
const salles = ref([]);
const plans = ref([]);



// --------------------------------------------------
// État de la page
// --------------------------------------------------

const loading = ref(false);
const errorMessage = ref("");

const actionEnCours = ref(null);



// --------------------------------------------------
// Équipement sélectionné
// --------------------------------------------------

const equipementSelectionne = ref(null);

const affectationEnCours = ref(false);

const formError = ref("");



// --------------------------------------------------
// Sélections du formulaire
// --------------------------------------------------

const batimentSelectionne = ref("");
const etageSelectionne = ref("");
const salleSelectionnee = ref("");
const planSelectionne = ref("");

const positionX = ref(0);
const positionY = ref(0);



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
// Filtrage des étages
// --------------------------------------------------

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



// --------------------------------------------------
// Filtrage des salles
// --------------------------------------------------

const sallesFiltrees = computed(() => {

    if (!etageSelectionne.value) {
        return [];
    }

    return salles.value.filter(
        (salle) =>
            String(salle.etage) ===
            String(etageSelectionne.value)
    );

});



// --------------------------------------------------
// Filtrage des plans
// --------------------------------------------------

const plansFiltres = computed(() => {

    if (!etageSelectionne.value) {
        return [];
    }

    return plans.value.filter(
        (plan) =>
            String(plan.etage) ===
            String(etageSelectionne.value)
    );

});



// --------------------------------------------------
// Chargement initial
// --------------------------------------------------

async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const [
            donneesEquipements,
            donneesBatiments,
            donneesEtages,
            donneesSalles,
            donneesPlans,
        ] = await Promise.all([

            getEquipementsDashboard(),
            getBatiments(),
            getEtages(),
            getSalles(),
            getPlans(),

        ]);

        equipements.value = donneesEquipements;

        batiments.value = donneesBatiments;
        etages.value = donneesEtages;
        salles.value = donneesSalles;
        plans.value = donneesPlans;

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

        const equipementModifie =
            await terminerMaintenance(
                equipement.id
            );

        remplacerEquipement(
            equipementModifie
        );

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
// Ouvrir le formulaire d'affectation
// --------------------------------------------------

function ouvrirFormulaireAffectation(
    equipement
) {

    equipementSelectionne.value =
        equipement;

    formError.value = "";

    batimentSelectionne.value = "";
    etageSelectionne.value = "";
    salleSelectionnee.value = "";
    planSelectionne.value = "";

    positionX.value = 0;
    positionY.value = 0;

}



// --------------------------------------------------
// Fermer le formulaire
// --------------------------------------------------

function fermerFormulaireAffectation() {

    equipementSelectionne.value =
        null;

    formError.value = "";

}



// --------------------------------------------------
// Changement de bâtiment
// --------------------------------------------------

function changerBatiment() {

    etageSelectionne.value = "";
    salleSelectionnee.value = "";
    planSelectionne.value = "";

}



// --------------------------------------------------
// Changement d'étage
// --------------------------------------------------

function changerEtage() {

    salleSelectionnee.value = "";
    planSelectionne.value = "";

}



// --------------------------------------------------
// Affectation
// --------------------------------------------------

async function affecter() {

    formError.value = "";

    if (!salleSelectionnee.value) {

        formError.value =
            "Veuillez sélectionner une salle.";

        return;

    }

    if (!planSelectionne.value) {

        formError.value =
            "Veuillez sélectionner un plan.";

        return;

    }

    if (
        positionX.value === null ||
        positionY.value === null
    ) {

        formError.value =
            "Les coordonnées X et Y sont obligatoires.";

        return;

    }

    affectationEnCours.value = true;

    try {

        const equipementModifie =
            await affecterEquipement(

                equipementSelectionne.value.id,

                salleSelectionnee.value,

                planSelectionne.value,

                positionX.value,

                positionY.value,

            );

        remplacerEquipement(
            equipementModifie
        );

        fermerFormulaireAffectation();

    } catch (error) {

        console.error(error);

        formError.value =
            error.response?.data?.detail ||
            "Impossible d'affecter l'équipement.";

    } finally {

        affectationEnCours.value = false;

    }

}



// --------------------------------------------------
// Remplace un équipement dans la liste
// --------------------------------------------------

function remplacerEquipement(
    equipementModifie
) {

    const index =
        equipements.value.findIndex(
            (equipement) =>
                equipement.id ===
                equipementModifie.id
        );

    if (index !== -1) {

        equipements.value[index] =
            equipementModifie;

    }

}



// --------------------------------------------------
// Affichage de la condition
// --------------------------------------------------

function afficherCondition(
    condition
) {

    const conditions = {

        NEUF: "Neuf",

        OCCASION: "Occasion",

        RECONDITIONNE:
            "Reconditionné",

    };

    return (
        conditions[condition] ||
        condition ||
        "Non renseignée"
    );

}



// --------------------------------------------------
// Affichage de l'état
// --------------------------------------------------

function afficherEtat(
    etat
) {

    const etats = {

        EN_SERVICE: "En service",

        EN_MAINTENANCE:
            "En maintenance",

        HORS_SERVICE:
            "Hors service",

    };

    return (
        etats[etat] ||
        etat ||
        "Inconnu"
    );

}



// --------------------------------------------------
// Classe CSS selon l'état
// --------------------------------------------------

function classeEtat(
    etat
) {

    return {

        "status-maintenance":
            etat === "EN_MAINTENANCE",

        "status-service":
            etat === "EN_SERVICE",

        "status-hors-service":
            etat === "HORS_SERVICE",

    };

}



// --------------------------------------------------
// Nom d'un étage
// --------------------------------------------------

function nomEtage(
    etageId
) {

    const etage =
        etages.value.find(
            (item) =>
                String(item.id) ===
                String(etageId)
        );

    return (
        etage?.nom ||
        `Étage ${etageId}`
    );

}



// --------------------------------------------------
// Initialisation
// --------------------------------------------------

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


.summary {
    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 20px;

    margin-bottom: 25px;
}


.summary-card {
    padding: 20px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 10px;

    display: flex;

    flex-direction: column;

    gap: 8px;
}


.summary-card strong {
    font-size: 28px;
}


.summary-label {
    color: #666;
}


.stock-container {
    display: flex;

    flex-direction: column;

    gap: 15px;
}


.stock-card {
    display: grid;

    grid-template-columns:
        1fr auto auto;

    gap: 25px;

    align-items: center;

    padding: 20px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 10px;
}


.equipment-info h2 {
    margin-top: 0;

    margin-bottom: 10px;
}


.equipment-info p {
    margin: 5px 0;

    color: #555;
}


.equipment-status {
    min-width: 140px;

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

    gap: 10px;
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


/* Modal */

.modal-overlay {
    position: fixed;

    inset: 0;

    z-index: 1000;

    display: flex;

    align-items: center;

    justify-content: center;

    padding: 20px;

    background: rgba(0, 0, 0, 0.45);
}


.modal {
    width: 100%;

    max-width: 600px;

    max-height: 90vh;

    overflow-y: auto;

    padding: 25px;

    background: white;

    border-radius: 12px;

    box-sizing: border-box;
}


.modal-header {
    display: flex;

    justify-content: space-between;

    align-items: flex-start;

    margin-bottom: 20px;
}


.modal-header h2 {
    margin: 0 0 5px 0;
}


.modal-header p {
    margin: 0;

    color: #666;
}


.close-button {
    border: none;

    background: none;

    font-size: 28px;

    cursor: pointer;

    color: #666;
}


.form-group {
    display: flex;

    flex-direction: column;

    margin-bottom: 15px;
}


.form-group label {
    margin-bottom: 6px;

    font-weight: 600;
}


.form-group select,
.form-group input {
    padding: 10px;

    border: 1px solid #ccc;

    border-radius: 6px;

    background: white;

    box-sizing: border-box;
}


.coordinates {
    display: grid;

    grid-template-columns:
        1fr 1fr;

    gap: 15px;
}


.modal-actions {
    display: flex;

    justify-content: flex-end;

    gap: 10px;

    margin-top: 20px;
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


@media (max-width: 600px) {

    .coordinates {
        grid-template-columns:
            1fr;
    }

}

</style>