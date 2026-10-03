<template>

    <div class="plan-viewer">

    <!-- Aucun plan -->

    <EmptyState
        v-if="!plan"
        titre="Aucun plan disponible"
        message="Sélectionnez un bâtiment puis un étage pour afficher son plan et la position des équipements."
    />

    <template v-else>

    <!--
        Contexte du plan : fil d'Ariane bâtiment > étage, compteur
        d'équipements, et légende des états représentés.

        Le plan est rattaché à un étage et non à une salle : le
        modèle `Plan` expose un lien vers `Etage` et aucun vers
        `Salle`, aucun niveau « salle » n'est donc affiché.
    -->

    <div class="plan-entete">

        <div class="plan-entete__contexte">

            <p
                v-if="filAriane.length > 0"
                class="plan-fil"
            >
                <template
                    v-for="(etape, index) in filAriane"
                    :key="etape"
                >
                    <span class="plan-fil__etape">
                        {{ etape }}
                    </span>

                    <span
                        v-if="index < filAriane.length - 1"
                        class="plan-fil__separateur"
                        aria-hidden="true"
                    >
                        ›
                    </span>
                </template>
            </p>

            <h2 class="plan-entete__titre">
                {{ libellePlan }}
            </h2>

            <p class="plan-entete__dimensions mono">
                {{ largeurPlan }} × {{ hauteurPlan }} px
            </p>
        </div>

        <p class="resultats-compte">
            <span class="resultats-compte__valeur">
                {{ positionsLocales.length }}
            </span>
            équipement(s) positionné(s) sur ce plan
        </p>
    </div>

    <!--
        Légende des états.

        Chaque état est identifié par un glyphe, une forme et un
        libellé : la couleur n'est jamais le seul indice.
    -->

    <section
        class="plan-legende"
        aria-labelledby="titre-legende-plan"
    >

        <h3
            id="titre-legende-plan"
            class="plan-legende__titre"
        >
            États sur le plan
        </h3>

        <ul class="plan-legende__liste">
            <li
                v-for="etat in etatsAffiches"
                :key="etat.valeur"
                class="plan-legende__item"
            >
                <span
                    class="plan-legende__glyphe"
                    :class="[etat.classe, 'forme-' + etat.forme]"
                    aria-hidden="true"
                >
                    {{ etat.glyphe }}
                </span>

                <span class="plan-legende__libelle">
                    {{ etat.libelle }}
                </span>

                <span class="plan-legende__compte">
                    {{ compteParEtat[etat.valeur] }}
                </span>
            </li>

            <li
                v-if="compteParEtat.__INCONNU > 0"
                class="plan-legende__item"
            >
                <span
                    class="plan-legende__glyphe forme-inconnu"
                    aria-hidden="true"
                >
                    ?
                </span>

                <span class="plan-legende__libelle">
                    État inconnu
                </span>

                <span class="plan-legende__compte">
                    {{ compteParEtat.__INCONNU }}
                </span>
            </li>
        </ul>
    </section>

    <!--
        Zone de défilement.

        Le conteneur porte le débordement, jamais le plan lui-même :
        `.plan-wrapper` conserve sa taille en pixels d'origine, qui
        est aussi l'espace de coordonnées des marqueurs. Aucune
        transformation ni mise à l'échelle ne doit être appliquée au
        plan, sous peine de désaligner les équipements.

        La sortie de zone est aussi écoutée au clavier (`@focusout`)
        : le comportement lié au survol ne doit pas rester réservé
        à la souris. Les deux appels visent la même fonction,
        `gererSortieDuPlan`.
    -->
    <div
        class="plan-zone-defilante"
    >

        <!-- Plan -->
        <div
            ref="planWrapper"
            class="plan-wrapper"
            :style="{
                width: largeurPlan + 'px',
                height: hauteurPlan + 'px'
            }"
            @mousemove="deplacerEquipement"
            @mouseup="terminerDeplacementGlobal"
            @mouseleave="gererSortieDuPlan"
            @focusout="gererSortieDuPlan"
            @dragover.prevent="
                survolDepotStock = true
            "
            @dragleave="
                survolDepotStock = false
            "
            @drop="
                survolDepotStock = false;
                if (props.estAdmin) {
                    deposerStockSurPlan($event)
                }
            "
        >

            <!-- Image du plan -->
            <img
                :src="urlImage"
                :alt="`Plan — ${libellePlan}`"
                class="plan-image"
                draggable="false"
            >


            <!--
                Équipements.

                La forme et le glyphe du marqueur portent l'état de
                l'équipement : la couleur ne les porte jamais seule.

                Le marqueur reste un `div` positionné en pixels par
                `:style` : le remplacer par un `button` Rompreait la
                géométrie et le glisser. Il est donc déclaré comme
                bouton et rendu atteignable au clavier.

                Le clic, Entrée et Espace appellent tous les trois
                `signalerClicSurMarqueur` : le glisser, lui, reste
                lié à `mousedown` et n'est jamais déclenché au
                clavier.
            -->
            <div
                v-for="position in positionsLocales"
                :key="position.id"
                class="equipement-marker"
                :class="[
                    etatPourPosition(position).classe,
                    'forme-' + etatPourPosition(position).forme,
                    {
                        'marker-selected':
                            positionSelectionnee?.id === position.id,
                        'marker-highlighted':
                            props.equipementAMettreEnEvidence &&
                            String(position.equipement) === String(props.equipementAMettreEnEvidence)
                    }
                ]"
                :style="{
                    left: position.x + 'px',
                    top: position.y + 'px'
                }"
                role="button"
                tabindex="0"
                :aria-label="titreMarqueur(position)"
                @mousedown.stop="
                    commencerDeplacement(position, $event)
                "
                @click.stop="
                    signalerClicSurMarqueur(position)
                "
                @keydown.enter.stop="
                    signalerClicSurMarqueur(position)
                "
                @keydown.space.prevent.stop="
                    signalerClicSurMarqueur(position)
                "
                :title="titreMarqueur(position)"
            >

                <span
                    class="marker-point"
                    aria-hidden="true"
                >
                    {{ etatPourPosition(position).glyphe }}
                </span>

                <span class="marker-label">
                    {{ position.equipement_nom }}

                    <span class="marker-etat">
                        {{ etatPourPosition(position).libelle }}
                    </span>
                </span>

                <!--
                    L'état est également porté par du texte lu par un
                    lecteur d'écran : le glyphe du marqueur est, lui,
                    masqué aux technologies d'assistance.
                -->
                <span class="visually-hidden">
                    — {{ etatPourPosition(position).libelle }}
                </span>

            </div>

            <!--
                Aucun équipement positionné : le plan reste affiché,
                l'information est donc superposée et non bloquante.
            -->
            <p
                v-if="positionsLocales.length === 0"
                class="plan-vide"
            >
                Aucun équipement positionné sur ce plan.
            </p>

            <!-- Marqueur de stock sur le plan -->
            <div
                v-if="props.estAdmin"
                class="plan-stock-marker"
                :class="{
                    'plan-stock-marker--drag': survolDepotStock
                }"
                :title="`${equipementsStock.length} équipement(s) en stock`"
            >
                <span
                    class="plan-stock-marker-icon"
                    aria-hidden="true"
                >
                    â–£
                </span>

                <span class="plan-stock-marker-label">
                    Stock
                </span>

                <span class="plan-stock-marker-count">
                    {{ chargementStock ? "…" : equipementsStock.length }}
                </span>
            </div>

            <!-- Indication de dépôt pendant un drag depuis le stock -->
            <div
                v-if="props.estAdmin && survolDepotStock"
                class="plan-drop-hint"
            >
                Déposez l'équipement sur le plan pour l'affecter
            </div>

        </div>
    </div>

    </template>

        <!--
            Zone de stockage (réservée aux administrateurs).

            Le nom de classe `stock-zone` est porteur de comportement :
            `terminerDeplacementGlobal` le recherche dans le document
            pour router un relâchement de souris vers le transfert. Il
            ne doit pas être renommé.
        -->

        <section
            v-if="props.estAdmin"
            class="stock-zone card"
            aria-labelledby="titre-stock-zone"
            @dragover.prevent
            @drop="deposerEquipementDansStock"
        >

            <div class="stock-header">

                <div>
                    <h3
                        id="titre-stock-zone"
                        class="stock-header__titre"
                    >
                        Stock
                    </h3>

                    <p class="stock-header__legende">
                        Équipements disponibles à réaffecter. Faites
                        glisser un équipement sur le plan pour le
                        positionner.
                    </p>
                </div>

                <div class="stock-header__actions">

                    <span class="stock-header__count">
                        <span class="stock-header__count-valeur">
                            {{ equipementsStock.length }}
                        </span>
                        équipement(s)
                    </span>

                    <!--
                        La maintenance ne peut être terminée que depuis
                        la console de stock : ce lien évite que
                        l'administrateur soit bloqué.
                    -->
                    <router-link
                        to="/stock"
                        class="btn-secondary btn-sm"
                    >
                        Gérer le stock
                    </router-link>

                </div>

            </div>

            <AppAlert
                v-if="equipementsEnMaintenance > 0"
                type="warning"
                :message="`${equipementsEnMaintenance} équipement(s) en attente de maintenance : ils ne peuvent pas être affectés tant que la maintenance n'est pas terminée.`"
            />

            <p
                v-if="chargementStock"
                class="stock-message"
                role="status"
            >
                <span
                    class="spinner spinner--compact"
                    aria-hidden="true"
                ></span>

                Chargement du stock…
            </p>


            <p
                v-else-if="equipementsStock.length === 0"
                class="stock-message text-muted"
            >
                Aucun équipement en stock.
            </p>


            <ul
                v-else
                class="stock-items"
            >

            <li
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

                <strong class="stock-item__nom">
                    {{ equipement.nom }}
                </strong>

                <span class="stock-item__inventaire mono">
                    {{ equipement.numero_inventaire }}
                </span>

                <!--
                    L'état est porté par la classe `etat-*` et par le
                    libellé texte : jamais par la seule couleur.
                -->
                <span
                    class="stock-item__etat"
                    :class="classeEtat(equipement.etat)"
                >
                    {{ libelleEtat(equipement.etat) }}
                </span>

                <small class="stock-item__condition">
                    {{ equipement.condition_stock }}
                </small>

            </li>

        </ul>

        </section>

        <!--
            Modale d'affectation.

            Elle est ouverte par le dépôt d'un équipement du stock sur
            le plan. Les identifiants de relation sont nécessaires aux
            attributs `aria-labelledby` / `aria-describedby`.

            Le clic sur le fond ferme la modale ; Échap fait de même.
            Le `.stop` évite que l'écouteur global de `surTouche` ne
            déclenche une seconde fois `annulerAffectation`.
        -->

        <div
            v-if="affichageChoixSalle"
            class="modal-overlay"
            @click.self="annulerAffectation"
            @keydown.esc.stop="annulerAffectation"
        >
            <div
                ref="modalAffectation"
                class="modal"
                role="dialog"
                aria-modal="true"
                tabindex="-1"
                aria-labelledby="titre-affectation"
                aria-describedby="description-affectation"
            >
                <h2
                    id="titre-affectation"
                    class="formulaire__titre"
                >
                    Affecter l'équipement
                </h2>

                <p
                    id="description-affectation"
                    class="modal-position"
                >
                    Choisissez la salle de destination. L'équipement sera
                    positionné aux coordonnées déposées sur le plan.
                </p>

                <p
                    v-if="equipementEnAttente"
                    class="modal-equipement"
                >
                    <strong>
                        {{ equipementEnAttente.nom }}
                    </strong>

                    <span
                        v-if="equipementEnAttente.numero_inventaire"
                        class="modal-equipement__inventaire mono"
                    >
                        {{ equipementEnAttente.numero_inventaire }}
                    </span>
                </p>

                <p class="modal-position">
                    Position sur le plan :
                    X = {{ positionStockEnAttente?.x }},
                    Y = {{ positionStockEnAttente?.y }}
                </p>

                <div class="form-group">
                    <label for="salle">
                        Salle
                    </label>

                    <select
                        id="salle"
                        v-model="salleSelectionnee"
                        :disabled="
                            chargementSalles ||
                            affectationEnCours ||
                            salles.length === 0
                        "
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

                    <p class="champ-aide">
                        Seules les salles de l'étage de ce plan sont
                        proposées.
                    </p>
                </div>

                <p
                    v-if="chargementSalles"
                    class="modal-info"
                    role="status"
                >
                    <span
                        class="spinner spinner--compact"
                        aria-hidden="true"
                    ></span>

                    Chargement des salles…
                </p>

                <p
                    v-else-if="salles.length === 0 && !messageAffectation"
                    class="modal-info"
                >
                    Aucune salle n'est enregistrée sur cet étage : un
                    équipement ne peut pas y être affecté tant qu'une
                    salle n'y a pas été créée.
                </p>

                <AppAlert
                    v-if="messageAffectation"
                    type="error"
                    :message="messageAffectation"
                />

                <div class="modal-actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        @click="annulerAffectation"
                        :disabled="affectationEnCours"
                    >
                        Annuler
                    </button>

                    <button
                        type="button"
                        class="btn-primary"
                        @click="confirmerAffectation"
                        :disabled="
                            !salleSelectionnee ||
                            affectationEnCours
                        "
                    >
                        {{
                            affectationEnCours
                                ? "Affectation…"
                                : "Affecter"
                        }}
                    </button>
                </div>
            </div>
        </div>

        <!--
            Équipement sélectionné : lecture pour tous, actions pour
            l'administrateur.

            Le panneau d'actions est distinct du simple déplacement
            d'un marqueur sur le plan : les deux gestes sont séparés
            explicitement, l'un par le glisser du marqueur, l'autre
            par ce panneau.
        -->

        <section
            v-if="positionSelectionnee"
            class="panneau-selection"
            aria-labelledby="titre-equipement-selectionne"
        >

            <div class="panneau-selection__identite">

                <h2
                    id="titre-equipement-selectionne"
                    class="panneau-selection__nom"
                >
                    {{ positionSelectionnee.equipement_nom }}
                </h2>

                <span
                    class="panneau-selection__etat"
                    :class="etatEquipementSelectionne.classe"
                >
                    {{ etatEquipementSelectionne.libelle }}
                </span>
            </div>

            <dl class="panneau-selection__coordonnees">
                <div class="panneau-selection__ligne">
                    <dt>Coordonnée X</dt>
                    <dd class="mono">
                        {{ positionSelectionnee.x }}
                    </dd>
                </div>

                <div class="panneau-selection__ligne">
                    <dt>Coordonnée Y</dt>
                    <dd class="mono">
                        {{ positionSelectionnee.y }}
                    </dd>
                </div>
            </dl>

            <!--
                Retour sur l'enregistrement d'un déplacement.
            -->
            <p
                v-if="sauvegardeEnCours"
                class="panneau-selection__message"
                role="status"
            >
                <span
                    class="spinner spinner--compact"
                    aria-hidden="true"
                ></span>

                Enregistrement…
            </p>

            <AppAlert
                v-else-if="messageSauvegarde"
                :type="sauvegardeReussie ? 'success' : 'error'"
                :message="messageSauvegarde"
            />

            <!--
                Actions d'administration.

                Le bouton appelle `deposerEquipementDansStock`, la
                fonction déjà utilisée par le dépôt sur la zone Stock :
                aucun appel API n'est ajouté, seule la façon de
                déclencher l'action change.

                Il n'existe volontairement pas de bouton « affecter »
                ici : l'affectation est determined par les coordonnées
                du dépôt, et la recomposer ici créerait une seconde
                logique de placement.
            -->
            <div
                v-if="props.estAdmin"
                class="panneau-selection__actions"
            >
                <button
                    type="button"
                    class="btn-delete btn-sm"
                    :disabled="sauvegardeEnCours"
                    @click="deposerEquipementDansStock"
                >
                    Envoyer vers le stock
                </button>
            </div>

            <p
                v-if="props.estAdmin"
                class="panneau-selection__aide"
            >
                Faites glisser le marqueur sur le plan pour modifier sa
                position, ou déposez-le sur la zone Stock pour le
                retirer du plan. Pour affecter un équipement du stock,
                faites-le glisser depuis la zone Stock jusqu'au plan.
            </p>
        </section>

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

import { getEquipementsDashboard } from "../services/dashboardService";
import { getSalles } from "../services/salleService";
import {
    transfererVersStock, affecterEquipement
} from "../services/stockService";

import AppAlert from "./AppAlert.vue";
import EmptyState from "./EmptyState.vue";
import { useFocusTrap } from "../composables/useFocusTrap";

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
     * ID de l'équipement à mettre en évidence.
     * Accepte un nombre ou une chaîne (paramètre d'URL).
     */
    equipementAMettreEnEvidence: {
        type: [Number, String],
        default: null,
    },

    /*
     * Bâtiments et étages, transmis par la vue publique.
     *
     * Ces deux props ne servent qu'à construire le fil d'Ariane. La
     * vue d'administration ne les fournit pas : le fil d'Ariane est
     * alors simplement omis, son en-tête restant inchangé.
     *
     * Les déclarer évite aussi que Vue ne les recopie en attributs
     * DOM sur l'élément racine.
     */
    batiments: {
        type: Array,
        default: () => [],
    },

    etages: {
        type: Array,
        default: () => [],
    },

});


/*
 * États d'équipement représentés sur le plan.
 *
 * Ces quatre valeurs sont celles du `TextChoices` `EtatEquipement`
 * côté Django. Aucune valeur n'est ajoutée ici.
 *
 * Le glyphe et la forme portent l'information : la couleur ne la
 * porte jamais seule.
 */
const etatsAffiches = [
    {
        valeur: "EN_SERVICE",
        libelle: "En service",
        glyphe: "âœ“",
        forme: "disque",
        classe: "etat-en_service",
    },
    {
        valeur: "EN_PANNE",
        libelle: "En panne",
        glyphe: "!",
        forme: "carre",
        classe: "etat-en_panne",
    },
    {
        valeur: "EN_MAINTENANCE",
        libelle: "En maintenance",
        glyphe: "âš™",
        forme: "disque-tronque",
        classe: "etat-en_maintenance",
    },
    {
        valeur: "HORS_SERVICE",
        libelle: "Hors service",
        glyphe: "âœ•",
        forme: "pilule",
        classe: "etat-hors_service",
    },
];

/*
 * État de repli lorsqu'un marqueur n'est rattaché à aucun équipement
 * connu du parent : le marqueur reste affiché, sans qu'un état lui
 * soit attribué.
 */
const etatInconnu = {
    valeur: "__INCONNU",
    libelle: "État inconnu",
    glyphe: "?",
    forme: "disque-tronque",
    classe: "etat-inconnu",
};


/*
 * Événements envoyés au parent.
 */
const emit = defineEmits([
    "position-modifiee",
    "equipement-clic",
]);


/*
 * Ouvre la fiche de l'équipement dont le marqueur est cliqué.
 * Utilisé par la vue publique pour afficher le détail.
 */
function signalerClicSurMarqueur(position) {
    const equipement = props.equipements.find(
        (item) =>
            String(item.id) ===
            String(position.equipement)
    );

    emit("equipement-clic", equipement ?? position);
}


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


/*
 * Libellé du plan.

 * Le modèle `Plan` n'expose aucun champ `nom` : le libellé est
 * reconstruit à partir de l'étage et du bâtiment lorsque la vue
 * publique les transmet, sinon il reste neutre.
 */
const libellePlan = computed(() => {
    if (!props.plan) {
        return "";
    }

    const etage = props.etages.find(
        (item) => String(item.id) === String(props.plan.etage)
    );

    if (etage?.nom) {
        return `Plan — ${etage.nom}`;
    }

    return "Plan du bâtiment";
});


/*
 * Fil d'Ariane bâtiment > étage.
 *
 * Le plan étant rattaché à un étage, aucun niveau « salle » n'existe
 * dans ce fil.
 */
const filAriane = computed(() => {
    if (!props.plan || props.etages.length === 0) {
        return [];
    }

    const etage = props.etages.find(
        (item) => String(item.id) === String(props.plan.etage)
    );

    if (!etage) {
        return [];
    }

    const batiment = props.batiments.find(
        (item) => String(item.id) === String(etage.batiment)
    );

    return [batiment?.nom, etage.nom].filter(Boolean);
});


/*
 * Équipement associé à une position.
 *
 * La position ne porte qu'un identifiant d'équipement : l'état est
 * lu sur la liste d'équipements fournie par le parent.
 */
function equipementPourPosition(position) {
    return (
        props.equipements.find(
            (item) =>
                String(item.id) === String(position.equipement)
        ) ?? null
    );
}


/*
 * État d'affichage d'un marqueur.
 */
function etatPourPosition(position) {
    const equipement = equipementPourPosition(position);

    if (!equipement?.etat) {
        return etatInconnu;
    }

    return (
        etatsAffiches.find(
            (etat) => etat.valeur === equipement.etat
        ) ?? etatInconnu
    );
}


/*
 * État de l'équipement sélectionné, pour le panneau d'actions.
 */
const etatEquipementSelectionne = computed(() => {
    if (!positionSelectionnee.value) {
        return etatInconnu;
    }

    return etatPourPosition(positionSelectionnee.value);
});


/*
 * Nombre d'équipements par état, pour la légende.
 */
const compteParEtat = computed(() => {
    const compte = { __INCONNU: 0 };

    for (const etat of etatsAffiches) {
        compte[etat.valeur] = 0;
    }

    for (const position of positionsLocales.value) {
        compte[etatPourPosition(position).valeur] += 1;
    }

    return compte;
});


/*
 * Libellé et classe d'un état, pour la zone Stock.
 */
function libelleEtat(etat) {
    return (
        etatsAffiches.find((item) => item.valeur === etat)
            ?.libelle ??
        etat ??
        "—"
    );
}

function classeEtat(etat) {
    return (
        etatsAffiches.find((item) => item.valeur === etat)
            ?.classe ?? "etat-inconnu"
    );
}


/*
 * Infobulle d'un marqueur : l'état y est nommé en toutes lettres.
 */
function titreMarqueur(position) {
    return (
        `${position.equipement_nom} — ` +
        etatPourPosition(position).libelle
    );
}

const equipementsStock = ref([]);
const chargementStock = ref(false);

/*
 * Indique que l'utilisateur survole le plan
 * avec un équipement issu du stock.
 */
const survolDepotStock = ref(false);

const salles = ref([]);
const chargementSalles = ref(false);

const equipementEnAttente = ref(null);
const positionStockEnAttente = ref(null);

const affichageChoixSalle = ref(false);

// Boîte de choix de salle : cible du piège de focus partagé.
const modalAffectation = ref(null);

/*
 * Cette modale s'ouvre au dépôt d'un équipement, opération à la souris :
 * le focus initial porte donc sur la boîte entière, pour annoncer le
 * titre et la position visée. Aucun déclencheur clavier n'ayant le focus
 * à ce moment-là, la restitution reste sans effet.
 */
useFocusTrap(modalAffectation, { focusInitial: "conteneur" });
const salleSelectionnee = ref("");
const affectationEnCours = ref(false);
const messageAffectation = ref("");

/*
 * Étage pour lequel les salles ont déjà été chargées.
 *
 * Sert uniquement à éviter un appel API inutile : le même étage est
 * rechargé si l'administrateur change de plan entre deux
 * affectations.
 */
const etageDesSallesChargees = ref(null);

/*
 * Équipements stockés dont la maintenance n'est pas terminée.
 *
 * Le backend force `etat = EN_MAINTENANCE` au transfert vers le stock
 * et refuse toute affectation tant que l'état n'est pas revenu à
 * EN_SERVICE. Ce compteur permet de signaler ce blocage au lieu de
 * laisser croire que l'équipement est simplement non déplaçable.
 */
const equipementsEnMaintenance = computed(
    () =>
        equipementsStock.value.filter(
            (equipement) =>
                equipement.etat === "EN_MAINTENANCE"
        ).length
);

/*
 * Watch sur le plan ET sur les positions.
 *
 * Suivre uniquement `props.plan` laissait des positions perimees
 * a l'ecran : le parent assignait le plan avant de charger les
 * positions, donc le filtre s'appliquait sur l'ancien plan et ne
 * se rejouait jamais quand les nouvelles positions arrivaient.
 */
watch(
    [() => props.plan, () => props.positions],
    async ([nouveauPlan, nouvellesPositions]) => {
        if (!nouveauPlan) {
            positionsLocales.value = [];
            return;
        }

        if (nouvellesPositions && nouvellesPositions.length > 0) {
            // Si les positions sont passées en prop, les utiliser
            positionsLocales.value = nouvellesPositions.filter(
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
    /*
     * Le stock n'est chargé que pour un admin :
     * la page publique n'appelle pas l'API.
     */
    if (props.estAdmin) {
        chargerStock();
    }

    document.addEventListener(
        "mouseup",
        terminerDeplacementGlobal
    );

    document.addEventListener(
        "keydown",
        surTouche
    );
});

onBeforeUnmount(() => {
    document.removeEventListener(
        "mouseup",
        terminerDeplacementGlobal
    );

    document.removeEventListener(
        "keydown",
        surTouche
    );
});

/*
 * Échap ferme la modale d'affectation, comme le fait
 * `ConfirmDialog` ailleurs dans l'application.
 */
function surTouche(event) {
    if (event.key === "Escape" && affichageChoixSalle.value) {
        annulerAffectation();
    }
}

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

/*
 * Charge les salles compatibles avec l'étage du plan courant.
 *
 * L'affectation passe nécessairement par une salle située sur le
 * même étage que le plan : un équipement ne peut pas être positionné
 * sur le plan d'un étage tout en étant affecté à une salle d'un
 * autre. Le modèle le permet sans modification du backend : `Plan`
 * porte un lien vers son `Etage`, `Salle` expose son `etage`, et le
 * `SalleViewSet` renvoie `fields = "__all__"`.
 *
 * L'endpoint n'accepte pas de filtre : le filtrage se fait donc
 * côté client, sur le modèle déjà appliqué par `Salles.vue`.
 *
 * L'appel est paresseux : il n'a lieu qu'à l'ouverture de la modale
 * d'affectation, et il est sauté si les salles de l'étage courant
 * sont déjà en mémoire.
 */
async function chargerSalles() {
    if (!props.estAdmin) {
        return;
    }

    const etageCourant = props.plan?.etage;

    if (!etageCourant) {
        /*
         * Sans étage rattaché, aucune salle ne peut être proposée
         * sans risquer d'affecter l'équipement à un autre étage.
         */
        salles.value = [];
        messageAffectation.value =
            "Ce plan n'est rattaché à aucun étage : impossible de déterminer les salles compatibles.";

        return;
    }

    if (
        etageDesSallesChargees.value !== null &&
        String(etageDesSallesChargees.value) === String(etageCourant)
    ) {
        return;
    }

    chargementSalles.value = true;
    messageAffectation.value = "";

    try {
        const toutesLesSalles = await getSalles();

        salles.value = toutesLesSalles.filter(
            (salle) =>
                String(salle.etage) === String(etageCourant)
        );

        etageDesSallesChargees.value = etageCourant;
    } catch (error) {
        console.error(
            "Erreur lors du chargement des salles :",
            error
        );

        salles.value = [];
        etageDesSallesChargees.value = null;

        messageAffectation.value =
            "Impossible de charger les salles de cet étage.";
    } finally {
        chargementSalles.value = false;
    }
}

/*
 * La modale d'affectation est ouverte par `deposerStockSurPlan`, qui
 * n'est pas modifié ici. Le chargement des salles est donc déclenché
 * à l'ouverture de la modale, et non dans cette fonction.
 */
watch(affichageChoixSalle, (ouverte) => {
    if (ouverte) {
        chargerSalles();
    }
});

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

/* =========================================================
   RAPPEL DE CONTRAINTE

   Le plan n'est pas un canvas : c'est une image de taille fixe
   dans laquelle des marqueurs sont positionnés en pixels. Les
   positions x/y enregistrées en base partagent exactement cet
   espace.

   Toute règle qui redimensionnerait `.plan-wrapper`, lui appliquerait
   une transformation, ou qui rendrait l'image à une taille
   différente décalerait les marqueurs et fausserait le
   glisser-déposer. Les règles ci-dessous respectent cette
   contrainte : seul le conteneur parent défile.
   ========================================================= */

.plan-viewer {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
}

/* --- Contexte du plan --- */

.plan-entete {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 0.75rem 1.5rem;
}

.plan-entete__contexte {
    min-width: 0;
}

.plan-fil {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.35rem;
    margin: 0 0 0.15rem;
    font-size: 0.8rem;
    color: var(--text-muted);
}

.plan-fil__separateur {
    color: var(--text-light);
}

.plan-entete__titre {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-main);
}

.plan-entete__dimensions {
    margin: 0.15rem 0 0;
    font-size: 0.75rem;
    color: var(--text-light);
}

/* --- Légende des états --- */

.plan-legende {
    padding: 0.75rem 0.9rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
}

.plan-legende__titre {
    margin: 0 0 0.6rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.plan-legende__liste {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.25rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.plan-legende__item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.8125rem;
    color: var(--text-muted);
}

.plan-legende__compte {
    padding: 0.05rem 0.4rem;
    background-color: var(--bg-subtle);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-main);
}

/* --- Zone de défilement --- */

.plan-zone-defilante {
    padding: 0.75rem;
    background-color: var(--bg-subtle);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    overflow: auto;
    max-height: 70vh;
}

/*
    Géométrie du plan : taille imposée en pixels par le style inline,
    position de référence des marqueurs. Ne pas modifier.
*/
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

/* --- Marqueurs --- */

.equipement-marker {
    position: absolute;
    transform: translate(-50%, -50%);
    z-index: 10;
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

/*
    Le point du marqueur reprend les couleurs de l'état via la
    classe `etat-*` du design system, mais impose sa propre forme :
    disque, carré, disque tronqué ou pilule. La forme et le glyphe
    portent donc l'information, la couleur vient en appui.
*/
.marker-point {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    padding: 0;
    font-size: 12px;
    line-height: 1;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.3);
    border: 2px solid #ffffff;
    text-transform: none;
    letter-spacing: normal;
}

.forme-disque {
    border-radius: 50%;
}

.forme-carre {
    border-radius: 2px;
}

.forme-disque-tronque {
    border-radius: 50%;
    border-style: dashed;
}

.forme-pilule {
    border-radius: var(--radius-full);
}

/*
    État non déterminable : l'équipement n'est pas présent dans la
    liste fournie par le parent. Ni found ni interpreté : un état
    n'est pas deviné.
*/
.etat-inconnu {
    background-color: var(--bg-surface);
    color: var(--text-muted);
    border: 1px dashed var(--border-medium);
}

.forme-inconnu {
    border-radius: 50%;
    border-style: dashed;
}

/* --- Fil d'Ariane --- */

.plan-fil__etape {
    font-weight: 600;
    color: var(--text-main);
}

/* --- Légende --- */

.plan-legende__glyphe {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    font-size: 11px;
    line-height: 1;
    text-transform: none;
    letter-spacing: normal;
    border: 1px solid transparent;
}

.plan-legende__libelle {
    white-space: nowrap;
}

/* --- Panneau de sélection --- */

.panneau-selection__etat {
    flex-shrink: 0;
}

.equipement-marker {
    cursor: grab;
}

.equipement-marker:active {
    cursor: grabbing;
}

.marker-label {
    position: absolute;
    left: 17px;
    top: -2px;
    display: flex;
    flex-direction: column;
    white-space: nowrap;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-sm);
    padding: 0.2rem 0.4rem;
    font-size: 11px;
    color: var(--text-main);
    box-shadow: var(--shadow-sm);
}

.marker-etat {
    font-size: 10px;
    color: var(--text-muted);
}

/* Aucun équipement sur le plan : superposition non bloquante. */

.plan-vide {
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
    margin: 0;
    padding: 0.6rem 1rem;
    background-color: rgba(255, 255, 255, 0.94);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: 0.85rem;
    pointer-events: none;
}

/* --- Marqueur de stock sur le plan --- */

.plan-stock-marker {
    position: absolute;
    top: 12px;
    right: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-full);
    font-size: 13px;
    color: var(--text-main);
    box-shadow: var(--shadow-md);
    z-index: 15;
    user-select: none;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.plan-stock-marker-icon {
    color: var(--primary);
    font-size: 15px;
}

.plan-stock-marker-label {
    font-weight: 600;
}

.plan-stock-marker-count {
    min-width: 22px;
    padding: 1px 7px;
    background-color: var(--primary);
    color: var(--on-primary);
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 600;
    text-align: center;
}

.plan-stock-marker--drag {
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-focus);
}

.plan-drop-hint {
    position: absolute;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    padding: 8px 16px;
    background-color: var(--primary);
    color: var(--on-primary);
    border-radius: var(--radius-full);
    font-size: 13px;
    font-weight: 600;
    pointer-events: none;
    z-index: 15;
}

/* --- Zone Stock --- */

.stock-zone {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    padding: 1rem 1.15rem;
}

.stock-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}

.stock-header__titre {
    margin: 0 0 0.15rem;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-main);
}

.stock-header__legende {
    margin: 0;
    max-width: 46ch;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.stock-header__actions {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem;
}

.stock-header__count {
    font-size: 0.8125rem;
    color: var(--text-muted);
}

.stock-header__count-valeur {
    font-weight: 700;
    color: var(--text-main);
}

.stock-items {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.stock-item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
    min-width: 165px;
    padding: 0.7rem 0.8rem;
    background-color: var(--bg-subtle);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
}

.stock-item__nom {
    font-size: 0.875rem;
    color: var(--text-main);
}

.stock-item__inventaire {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.stock-item__etat {
    font-size: 0.6875rem;
}

.stock-item__condition {
    color: var(--text-muted);
    font-size: 0.75rem;
}

.stock-item-disabled {
    opacity: 0.55;
    cursor: not-allowed;
}

.stock-item:not(.stock-item-disabled) {
    cursor: grab;
}

.stock-item:not(.stock-item-disabled):active {
    cursor: grabbing;
}

.stock-message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    color: var(--text-muted);
    font-size: 0.875rem;
}

/* --- Panneau de l'équipement sélectionné --- */

.panneau-selection {
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    padding: 1rem 1.15rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.panneau-selection__identite {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.6rem;
}

.panneau-selection__nom {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-main);
}

.panneau-selection__coordonnees {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem 1.5rem;
    margin: 0;
}

.panneau-selection__ligne {
    display: flex;
    align-items: baseline;
    gap: 0.4rem;
}

.panneau-selection__ligne dt {
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.panneau-selection__ligne dd {
    margin: 0;
    font-weight: 600;
}

.panneau-selection__message {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.panneau-selection__actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    padding-top: 0.85rem;
    border-top: 1px solid var(--border-light);
}

.panneau-selection__aide {
    margin: 0;
    max-width: 62ch;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

/* --- Modale d'affectation --- */

.modal {
    width: 100%;
    max-width: 460px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 1.5rem;
    background-color: var(--bg-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
}

.modal-position {
    margin: 0 0 0.75rem;
    color: var(--text-muted);
    font-size: 0.85rem;
}

.modal-equipement {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    margin: 0 0 0.75rem;
    padding: 0.6rem 0.75rem;
    background-color: var(--bg-subtle);
    border-radius: var(--radius-md);
}

.modal-equipement__inventaire {
    font-size: 0.75rem;
    color: var(--text-muted);
}

.modal-info {
    margin: 0.5rem 0 0;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.champ-aide {
    margin: 0.35rem 0 0;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.modal-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.5rem;
    margin-top: 1.1rem;
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}

.spinner--compact {
    width: 1rem;
    height: 1rem;
    border-width: 2px;
}

/* --- Responsive --- */

@media (max-width: 900px) {
    .plan-zone-defilante {
        max-height: 55vh;
    }
}

@media (max-width: 640px) {
    .plan-legende__liste {
        gap: 0.4rem 0.9rem;
    }

    .plan-entete {
        flex-direction: column;
        align-items: flex-start;
    }

    .stock-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .panneau-selection__actions {
        flex-direction: column;
        align-items: stretch;
    }

    .panneau-selection__actions > * {
        width: 100%;
    }

    .modal-actions {
        flex-direction: column-reverse;
    }

    .modal-actions > * {
        width: 100%;
    }
}
</style>
