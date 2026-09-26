<template>

    <div class="plan-container">

        <!-- Aucun plan -->
        <div
            v-if="!plan"
            class="empty"
        >
            Aucun plan disponible.
        </div>


        <!-- Plan -->
        <div
            v-else
            ref="planWrapper"
            class="plan-wrapper"
            :style="{
                width: largeurPlan + 'px',
                height: hauteurPlan + 'px'
            }"
            @mousemove="deplacerEquipement"
            @mouseup="terminerDeplacementGlobal"
            @mouseleave="gererSortieDuPlan"
            @dragover.prevent
            @drop="deposerStockSurPlan"
        >

            <!-- Image du plan -->
            <img
                :src="urlImage"
                alt="Plan de l'étage"
                class="plan-image"
                draggable="false"
            >


            <!-- Équipements -->
            <div
                v-for="position in positionsLocales"
                :key="position.id"
                class="equipement-marker"
                :class="{
                    'marker-selected':
                        positionSelectionnee?.id === position.id,
                    'marker-highlighted':
                        props.equipementAMettreEnEvidence &&
                        String(position.equipement) === String(props.equipementAMettreEnEvidence)
                }"
                :style="{
                    left: position.x + 'px',
                    top: position.y + 'px'
                }"
                @mousedown.stop="
                    commencerDeplacement(position, $event)
                "
                :title="position.equipement_nom"
            >

                <span class="marker-point">
                    ●
                </span>

                <span class="marker-label">
                    {{ position.equipement_nom }}
                </span>

            </div>

        </div>

        <!-- Zone de stockage -->

        <div class="stock-zone"
        @dragover.prevent
        @drop="deposerEquipementDansStock"
        >

            <div class="stock-header">

                <div>
                    <h3>Stock</h3>

                <p>
                    Équipements disponibles
                </p>
                </div>

                <span>
                {{ equipementsStock.length }}
                équipement(s)
                </span>

            </div>


            <p
                v-if="chargementStock"
                class="stock-message"
            >
                Chargement du stock...
            </p>


            <p
                v-else-if="equipementsStock.length === 0"
                class="stock-message"
            >
                Aucun équipement en stock.
            </p>


            <div
                v-else
                class="stock-items"
            >

            <div
                v-for="equipement in equipementsStock"
                :key="equipement.id"
                class="stock-item"
                :class="{
                    'stock-item-disabled':
                    equipement.etat !== 'EN_SERVICE'
                }"
                :draggable="equipement.etat === 'EN_SERVICE'"
                @dragstart="commencerDragStock($event, equipement)"
            >

                <strong>
                    {{ equipement.nom }}
                </strong>

                <span>
                    {{ equipement.numero_inventaire }}
                </span>

                <small>
                    {{ equipement.condition_stock }}
                </small>

            </div>

        </div>

        <div
            v-if="affichageChoixSalle"
            class="modal-overlay"
        >
            <div class="modal">
                <h3>Affecter l'équipement</h3>

                <p v-if="equipementEnAttente">
                    <strong>
                        {{ equipementEnAttente.nom }}
                    </strong>
                </p>

                <p class="modal-position">
                Position :
                X = {{ positionStockEnAttente?.x }},
                Y = {{ positionStockEnAttente?.y }}
                </p>

                <label for="salle">
                    Salle
                </label>

                <select
                    id="salle"
                    v-model="salleSelectionnee"
                    :disabled="chargementSalles || affectationEnCours"
                >
                    <option value="">
                        -- Sélectionner une salle --
                    </option>

                    <option
                        v-for="salle in salles"
                        :key="salle.id"
                        :value="salle.id"
                    >
                        {{ salle.nom }}
                    </option>
                </select>

                <p
                    v-if="chargementSalles"
                    class="modal-info"
                >
                    Chargement des salles...
                </p>

                <p
                    v-if="messageAffectation"
                    class="message-error"
                >
                    {{ messageAffectation }}
                </p>

                <div class="modal-actions">
                    <button
                        type="button"
                        @click="annulerAffectation"
                        :disabled="affectationEnCours"
                    >
                    Annuler
                    </button>

                    <button
                        type="button"
                        @click="confirmerAffectation"
                        :disabled="
                            !salleSelectionnee ||
                            affectationEnCours
                        "
                    >
                        {{
                            affectationEnCours
                                ? "Affectation..."
                                : "Affecter"
                        }}
                    </button>
                </div>
            </div>
        </div>

    </div>


        <!-- Informations sur l'équipement sélectionné -->
        <div
            v-if="positionSelectionnee"
            class="position-info"
        >

            <strong>
                {{ positionSelectionnee.equipement_nom }}
            </strong>

            <span>
                X : {{ positionSelectionnee.x }}
            </span>

            <span>
                Y : {{ positionSelectionnee.y }}
            </span>

            <span v-if="sauvegardeEnCours">
                Enregistrement...
            </span>

            <span
                v-else-if="messageSauvegarde"
                :class="{
                    'message-success':
                        sauvegardeReussie,
                    'message-error':
                        !sauvegardeReussie
                }"
            >
                {{ messageSauvegarde }}
            </span>

        </div>

    </div>

</template>


<script setup>

import {
    computed,
    ref,
    watch,
    onMounted,
    onBeforeUnmount
} from "vue";

import {
    deplacerEquipement as sauvegarderDeplacement, getPositionsParPlan
} from "../services/localisationService";

import { getEquipementsDashboard, getSallesDashboard } from "../services/dashboardService";
import {
    transfererVersStock, affecterEquipement
} from "../services/stockService";

/*
 * Props reçues depuis Localisation.vue.
 */
const props = defineProps({

    plan: {
        type: Object,
        default: null,
    },

    positions: {
        type: Array,
        default: () => [],
    },

    equipements: {
        type: Array,
        default: () => [],
    },

    /*
     * Seul un administrateur peut déplacer
     * les équipements.
     */
    estAdmin: {
        type: Boolean,
        default: false,
    },

    /*
     * ID de l'équipement à mettre en évidence
     */
    equipementAMettreEnEvidence: {
        type: Number,
        default: null,
    },

});


/*
 * Événements envoyés au parent.
 */
const emit = defineEmits([
    "position-modifiee",
]);


/*
 * Copie locale des positions.
 *
 * On évite de modifier directement
 * les objets reçus dans les props.
 */
const positionsLocales = ref([]);


/*
 * Synchronisation avec les positions
 * reçues depuis Localisation.vue.
 */
const planWrapper = ref(null);


/*
 * Position actuellement sélectionnée.
 */
const positionSelectionnee = ref(null);


/*
 * Ancienne position avant déplacement.
 *
 * Elle permet de revenir en arrière
 * si l'enregistrement échoue.
 */
const anciennePosition = ref(null);


/*
 * État du déplacement.
 */
const deplacementEnCours = ref(false);


/*
 * État de sauvegarde.
 */
const sauvegardeEnCours = ref(false);


/*
 * Message après sauvegarde.
 */
const messageSauvegarde = ref("");


/*
 * Indique si la dernière sauvegarde
 * a réussi.
 */
const sauvegardeReussie = ref(false);


/*
 * Dimensions du plan.
 */
const largeurPlan = computed(() => {
    return props.plan?.largeur || 1000;
});

const hauteurPlan = computed(() => {
    return props.plan?.hauteur || 700;
});


/*
 * URL de l'image du plan.
 */
const urlImage = computed(() => {

    if (!props.plan?.image) {
        return "";
    }

    if (props.plan.image.startsWith("http")) {
        return props.plan.image;
    }

    return `http://127.0.0.1:8000${props.plan.image}`;

});

const equipementsStock = ref([]);
const chargementStock = ref(false);
const salles = ref([]);
const chargementSalles = ref(false);

const equipementEnAttente = ref(null);
const positionStockEnAttente = ref(null);

const affichageChoixSalle = ref(false);
const salleSelectionnee = ref("");
const affectationEnCours = ref(false);
const messageAffectation = ref("");

/*
 * Watch sur le plan pour charger les positions
 */
watch(
    () => props.plan,
    async (nouveauPlan) => {
        if (!nouveauPlan) {
            positionsLocales.value = [];
            return;
        }

        if (props.positions && props.positions.length > 0) {
            // Si les positions sont passées en prop, les utiliser
            positionsLocales.value = props.positions.filter(
                (position) => String(position.plan) === String(nouveauPlan.id)
            );
        } else {
            // Sinon, les charger depuis l'API
            try {
                const positions = await getPositionsParPlan(nouveauPlan.id);
                positionsLocales.value = positions;
            } catch (error) {
                console.error("Erreur lors du chargement des positions:", error);
                positionsLocales.value = [];
            }
        }
    },
    { immediate: true }
);

/*
 * Commence le déplacement d'un équipement.
 */
function commencerDeplacement(position, event) {
    if (!props.estAdmin) {
        return;
    }

    positionSelectionnee.value = position;
    anciennePosition.value = { x: position.x, y: position.y };
    deplacementEnCours.value = true;
}

/*
 * Déplacement visuel du marqueur.
 */
function deplacerEquipement(event) {

    if (!deplacementEnCours.value) {
        return;
    }

    if (!positionSelectionnee.value) {
        return;
    }

    if (!planWrapper.value) {
        return;
    }


    const rect =
        planWrapper.value.getBoundingClientRect();


    /*
     * Coordonnées relatives au plan.
     */
    let x =
        event.clientX - rect.left;

    let y =
        event.clientY - rect.top;


    /*
     * Empêche le marqueur de sortir
     * des limites du plan.
     */
    x = Math.max(
        0,
        Math.min(
            x,
            largeurPlan.value
        )
    );

    y = Math.max(
        0,
        Math.min(
            y,
            hauteurPlan.value
        )
    );


    /*
     * Mise à jour locale.
     */
    positionSelectionnee.value.x =
        Math.round(x);

    positionSelectionnee.value.y =
        Math.round(y);

}


/*
 * Termine le déplacement.
 */
async function terminerDeplacement() {

    if (!deplacementEnCours.value) {
        return;
    }

    if (!positionSelectionnee.value) {
        return;
    }


    deplacementEnCours.value = false;


    const position =
        positionSelectionnee.value;


    sauvegardeEnCours.value = true;

    messageSauvegarde.value = "";


    try {

        /*
         * Appel de l'API Django.
         */
        const positionModifiee =
            await sauvegarderDeplacement(
                position.id,
                position.plan,
                position.x,
                position.y
            );


        /*
         * Mise à jour avec les données
         * réellement retournées par Django.
         */
        Object.assign(
            position,
            positionModifiee
        );


        messageSauvegarde.value =
            "Position enregistrée.";

        sauvegardeReussie.value = true;


        /*
         * Informe le composant parent.
         */
        emit(
            "position-modifiee",
            positionModifiee
        );


    } catch (error) {

        console.error(
            "Erreur lors de la sauvegarde :",
            error
        );


        /*
         * Retour à la position précédente.
         */
        if (anciennePosition.value) {

            position.x =
                anciennePosition.value.x;

            position.y =
                anciennePosition.value.y;

        }


        messageSauvegarde.value =
            error.response?.data?.detail ||
            "Erreur lors de l'enregistrement.";

        sauvegardeReussie.value = false;


    } finally {

        sauvegardeEnCours.value = false;

    }

}

async function chargerStock() {
    chargementStock.value = true;

    try {
        const equipements = await getEquipementsDashboard();

        equipementsStock.value = equipements.filter(
            (equipement) =>
                equipement.situation === "EN_STOCK"
        );

    } catch (error) {
        console.error(
            "Erreur lors du chargement du stock :",
            error
        );
    } finally {
        chargementStock.value = false;
    }
}

function commencerDragStock(event, equipement) {
    // Un équipement en maintenance ne peut pas être affecté.
    if (equipement.etat !== "EN_SERVICE") {
        event.preventDefault();
        return;
    }

    event.dataTransfer.effectAllowed = "move";

    event.dataTransfer.setData(
        "application/json",
        JSON.stringify({
            equipementId: equipement.id,
        })
    );
}

onMounted(() => {
    chargerStock();

    document.addEventListener(
        "mouseup",
        terminerDeplacementGlobal
    );
});

onBeforeUnmount(() => {
    document.removeEventListener(
        "mouseup",
        terminerDeplacementGlobal
    );
});

async function terminerDeplacementGlobal(event) {

    if (!deplacementEnCours.value) {
        return;
    }

    const stockZone =
        document.querySelector(".stock-zone");

    /*
     * Si le relâchement se produit
     * dans la zone Stock.
     */
    if (
        stockZone &&
        stockZone.contains(event.target)
    ) {
        await deposerEquipementDansStock();
        return;
    }

    /*
     * Sinon, il s'agit d'un déplacement
     * normal sur le plan.
     */
    await terminerDeplacement();
}

function deposerStockSurPlan(event) {
    if (!props.estAdmin) return;

    const donnees = event.dataTransfer.getData(
        "application/json"
    );

    if (!donnees) return;

    let data;

    try {
        data = JSON.parse(donnees);
    } catch (error) {
        console.error(
            "Données de déplacement invalides :",
            error
        );
        return;
    }

    const equipement = equipementsStock.value.find(
        (item) =>
            item.id === data.equipementId
    );

    if (!equipement) return;

    if (equipement.etat !== "EN_SERVICE") {
        messageAffectation.value =
            "Cet équipement doit être en service avant son affectation.";

        return;
    }

    if (!planWrapper.value) return;

    const rect =
        planWrapper.value.getBoundingClientRect();

    let x = event.clientX - rect.left;
    let y = event.clientY - rect.top;

    x = Math.max(
        0,
        Math.min(x, largeurPlan.value)
    );

    y = Math.max(
        0,
        Math.min(y, hauteurPlan.value)
    );

    equipementEnAttente.value = equipement;

    positionStockEnAttente.value = {
        x: Math.round(x),
        y: Math.round(y),
    };

    salleSelectionnee.value = "";
    messageAffectation.value = "";
    affichageChoixSalle.value = true;
}

function gererSortieDuPlan() {

    /*
     * Si aucun déplacement n'est en cours,
     * rien à faire.
     */
    if (!deplacementEnCours.value) {
        return;
    }

    /*
     * On ne sauvegarde pas immédiatement.
     *
     * L'utilisateur peut être en train
     * de déplacer l'équipement vers le stock.
     */
}

async function deposerEquipementDansStock() {

    if (!positionSelectionnee.value) {
        return;
    }

    const position =
        positionSelectionnee.value;

    const equipementId =
        position.equipement;

    try {

        /*
         * Pour l'instant on utilise
         * OCCASION comme valeur par défaut.
         *
         * On améliorera ensuite avec
         * une vraie sélection dans une modal.
         */
        const equipement =
            await transfererVersStock(
                equipementId,
                "OCCASION"
            );

        /*
         * Suppression de la position
         * de l'affichage local.
         */
        positionsLocales.value =
            positionsLocales.value.filter(
                (item) =>
                    item.id !== position.id
            );

        /*
         * Ajout au stock local.
         */
        equipementsStock.value.push(
            equipement
        );

        positionSelectionnee.value = null;

        deplacementEnCours.value = false;

        messageSauvegarde.value =
            "Équipement transféré vers le stock.";

        sauvegardeReussie.value = true;

    } catch (error) {

        console.error(
            "Erreur lors du transfert vers le stock :",
            error
        );

        messageSauvegarde.value =
            error.response?.data?.detail ||
            "Impossible de transférer l'équipement vers le stock.";

        sauvegardeReussie.value = false;

    }
}

async function confirmerAffectation() {
    if (!equipementEnAttente.value) return;

    if (!salleSelectionnee.value) {
        messageAffectation.value =
            "Veuillez sélectionner une salle.";

        return;
    }

    if (!positionStockEnAttente.value) return;

    affectationEnCours.value = true;
    messageAffectation.value = "";

    try {
        await affecterEquipement(
            equipementEnAttente.value.id,
            salleSelectionnee.value,
            props.plan.id,
            positionStockEnAttente.value.x,
            positionStockEnAttente.value.y
        );

        // Recharge les positions du plan.
        positionsLocales.value =
            await getPositionsParPlan(
                props.plan.id
            );

        // Retire l'équipement du stock local.
        equipementsStock.value =
            equipementsStock.value.filter(
                (equipement) =>
                    equipement.id !==
                    equipementEnAttente.value.id
            );

        messageAffectation.value =
            "Équipement affecté avec succès.";

        affichageChoixSalle.value = false;

        equipementEnAttente.value = null;
        positionStockEnAttente.value = null;
        salleSelectionnee.value = "";
    } catch (error) {
        console.error(
            "Erreur lors de l'affectation :",
            error
        );

        messageAffectation.value =
            error.response?.data?.detail ||
            "Impossible d'affecter l'équipement.";
    } finally {
        affectationEnCours.value = false;
    }
}

function annulerAffectation() {
    affichageChoixSalle.value = false;

    equipementEnAttente.value = null;
    positionStockEnAttente.value = null;
    salleSelectionnee.value = "";
    messageAffectation.value = "";
}
</script>


<style scoped>

.plan-container {
    width: 100%;

    overflow: auto;

    border: 1px solid #ddd;
    border-radius: 10px;

    background: #f5f5f5;

    padding: 20px;

    box-sizing: border-box;
}


.plan-wrapper {
    position: relative;

    margin: auto;

    user-select: none;
}


.plan-image {
    display: block;

    width: 100%;
    height: 100%;

    object-fit: contain;

    user-select: none;

    pointer-events: none;
}


.equipement-marker {
    position: absolute;

    transform: translate(-50%, -50%);

    cursor: grab;

    z-index: 10;
}


.equipement-marker:active {
    cursor: grabbing;
}


.marker-selected {
    z-index: 20;
}

.marker-highlighted {
    z-index: 20;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% {
        transform: translate(-50%, -50%) scale(1);
    }
    50% {
        transform: translate(-50%, -50%) scale(1.3);
    }
}

.marker-point {
    font-size: 25px;
}


.marker-label {
    position: absolute;

    left: 15px;
    top: 0;

    white-space: nowrap;

    background: white;

    border: 1px solid #ddd;

    border-radius: 5px;

    padding: 4px 7px;

    font-size: 12px;

    box-shadow:
        0 2px 5px rgba(0, 0, 0, 0.15);
}


.position-info {
    margin-top: 15px;

    padding: 10px;

    display: flex;

    gap: 15px;

    align-items: center;

    background: white;

    border: 1px solid #ddd;

    border-radius: 8px;
}


.message-success {
    color: #16803c;
}


.message-error {
    color: #b00020;
}


.empty {
    padding: 40px;

    text-align: center;

    color: #666;
}

.stock-zone {
    margin-top: 20px;

    padding: 20px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 10px;
}


.stock-header {
    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 15px;
}


.stock-header h3 {
    margin: 0 0 5px 0;
}


.stock-header p {
    margin: 0;

    color: #666;
}


.stock-header > span {
    color: #666;

    font-size: 14px;
}


.stock-items {
    display: flex;

    flex-wrap: wrap;

    gap: 12px;
}


.stock-item {
    display: flex;

    flex-direction: column;

    gap: 4px;

    min-width: 150px;

    padding: 12px;

    background: #f5f5f5;

    border: 1px solid #ddd;

    border-radius: 8px;
}


.stock-item strong {
    font-size: 14px;
}


.stock-item span {
    font-size: 13px;

    color: #555;
}


.stock-item small {
    color: #777;
}


.stock-message {
    margin: 0;

    color: #666;
}

.stock-item-disabled {
    opacity: 0.5;

    cursor: not-allowed;
}

.stock-item:not(.stock-item-disabled) {
    cursor: grab;
}

.stock-item:not(.stock-item-disabled):active {
    cursor: grabbing;
}

.modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;

    display: flex;
    justify-content: center;
    align-items: center;

    background: rgba(0, 0, 0, 0.45);
}

.modal {
    width: 400px;
    max-width: 90%;

    padding: 25px;

    background: white;
    border-radius: 10px;

    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.25);
}

.modal h3 {
    margin-top: 0;
    margin-bottom: 15px;
}

.modal p {
    margin: 8px 0;
}

.modal-position {
    color: #666;
    font-size: 14px;
}

.modal label {
    display: block;
    margin-top: 20px;
    margin-bottom: 6px;

    font-weight: 600;
}

.modal select {
    width: 100%;
    padding: 10px;

    border: 1px solid #ccc;
    border-radius: 6px;

    background: white;
}

.modal-info {
    color: #666;
    font-size: 13px;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;

    margin-top: 25px;
}

.modal-actions button {
    padding: 9px 16px;

    border: 1px solid #ccc;
    border-radius: 6px;

    cursor: pointer;
}

.modal-actions button:last-child {
    color: white;
    background: #2563eb;
    border-color: #2563eb;
}

.modal-actions button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>