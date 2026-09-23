<template>
    <div class="plan-container">

        <div v-if="!plan" class="empty">
            Aucun plan disponible.
        </div>

        <div
            v-else
            ref="planWrapper"
            class="plan-wrapper"
            :style="{
                width: largeurPlan + 'px',
                height: hauteurPlan + 'px'
            }"
            @mousemove="deplacerEquipement"
            @mouseup="terminerDeplacement"
            @mouseleave="terminerDeplacement"
        >

            <img
                :src="urlImage"
                alt="Plan de l'étage"
                class="plan-image"
                draggable="false"
            >

            <div
                v-for="position in positions"
                :key="position.id"
                class="equipement-marker"
                :class="{
                    'marker-selected':
                        positionSelectionnee?.id === position.id
                }"
                :style="{
                    left: position.x + 'px',
                    top: position.y + 'px'
                }"
                @mousedown.stop="commencerDeplacement(position, $event)"
                :title="position.equipement_nom"
            >
                <span class="marker-point">●</span>

                <span class="marker-label">
                    {{ position.equipement_nom }}
                </span>
            </div>

        </div>

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

            <span v-if="messageSauvegarde">
                {{ messageSauvegarde }}
            </span>
        </div>

    </div>
    
</template>

<script setup>
import { computed, ref } from "vue";
import { modifierPosition } from "../services/localisationService";

/*
 * Props reçues depuis Localisation.vue
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

    /*
     * Permet de savoir si l'utilisateur est administrateur.
     * Un utilisateur normal pourra consulter le plan
     * mais ne pourra pas déplacer les équipements.
     */
    estAdmin: {
        type: Boolean,
        default: false,
    },
});

/*
 * Référence vers le conteneur du plan.
 */
const planWrapper = ref(null);

/*
 * Position actuellement sélectionnée.
 */
const positionSelectionnee = ref(null);

/*
 * Indique si un équipement est actuellement déplacé.
 */
const deplacementEnCours = ref(false);

/*
 * Indique si la sauvegarde est en cours.
 */
const sauvegardeEnCours = ref(false);

/*
 * Message affiché après sauvegarde.
 */
const messageSauvegarde = ref("");

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
 * Construction de l'URL de l'image.
 *
 * Si Django renvoie une URL complète :
 *     http://127.0.0.1:8000/media/...
 *
 * on l'utilise directement.

 * Si Django renvoie seulement :
 *     /media/...
 *
 * on ajoute l'adresse du backend.
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


/*
 * Commence le déplacement d'un équipement.
 */
function commencerDeplacement(position, event) {

    /*
     * Seul l'administrateur peut déplacer
     * les équipements.
     */
    if (!props.estAdmin) {
        return;
    }

    positionSelectionnee.value = position;
    deplacementEnCours.value = true;

    messageSauvegarde.value = "";

    event.preventDefault();
}


/*
 * Déplace visuellement l'équipement
 * pendant que la souris bouge.
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

    const rect = planWrapper.value.getBoundingClientRect();

    /*
     * Calcul des coordonnées relatives
     * au plan.
     */
    let x = event.clientX - rect.left;
    let y = event.clientY - rect.top;

    /*
     * Empêche le marqueur de sortir du plan.
     */
    x = Math.max(0, Math.min(x, largeurPlan.value));
    y = Math.max(0, Math.min(y, hauteurPlan.value));

    /*
     * Mise à jour locale.
     *
     * Vue met automatiquement le marqueur
     * à la nouvelle position.
     */
    positionSelectionnee.value.x = Math.round(x);
    positionSelectionnee.value.y = Math.round(y);
}


/*
 * Termine le déplacement et sauvegarde
 * la nouvelle position dans Django.
 */
async function terminerDeplacement() {

    if (!deplacementEnCours.value) {
        return;
    }

    if (!positionSelectionnee.value) {
        return;
    }

    deplacementEnCours.value = false;

    const position = positionSelectionnee.value;

    sauvegardeEnCours.value = true;
    messageSauvegarde.value = "";

    try {

        await modifierPosition(position.id, {
            equipement: position.equipement,
            plan: position.plan,
            x: position.x,
            y: position.y,
        });

        messageSauvegarde.value = "Position enregistrée.";

    } catch (error) {

        console.error(
            "Erreur lors de la sauvegarde de la position :",
            error
        );

        messageSauvegarde.value =
            "Erreur lors de l'enregistrement.";

    } finally {

        sauvegardeEnCours.value = false;
    }
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

    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15);
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

.empty {
    padding: 40px;
    text-align: center;
    color: #666;
}

</style>