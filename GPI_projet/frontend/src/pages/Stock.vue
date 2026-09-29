<template>
    <div class="page-container stock-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Stock et maintenance
                </h1>

                <p class="page-heading__subtitle">
                    Équipements en attente d'affectation et interventions
                    en cours.
                </p>
            </div>

            <div class="page-heading__actions">
                <!--
                    L'affectation et le placement sur le plan relèvent
                    de PlanViewer : cette page y renvoie sans le
                    remplacer.
                -->
                <router-link
                    to="/localisation"
                    class="btn-secondary"
                >
                    Affecter sur le plan
                </router-link>
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
            titre="Chargement du stock…"
        />

        <template v-else-if="!errorMessage">
            <!--
                Résumé : les trois compteurs sont calculés à partir de
                la liste déjà chargée. Aucun appel supplémentaire.
            -->

            <section
                class="statistiques"
                aria-label="Situation du stock"
            >
                <div class="statistique">
                    <span class="statistique__intitule">
                        En stock
                    </span>

                    <span class="statistique__valeur">
                        {{ equipementsStock.length }}
                    </span>
                </div>

                <div
                    class="statistique"
                    :class="{ 'statistique--alerte': nombreEnMaintenance > 0 }"
                >
                    <span class="statistique__intitule">
                        En maintenance
                    </span>

                    <span class="statistique__valeur">
                        {{ nombreEnMaintenance }}
                    </span>

                    <span
                        v-if="nombreEnMaintenance > 0"
                        class="statistique__detail"
                    >
                        Intervention à clôturer
                    </span>
                </div>

                <div class="statistique">
                    <span class="statistique__intitule">
                        Prêts à être affectés
                    </span>

                    <span class="statistique__valeur">
                        {{ nombrePrets }}
                    </span>
                </div>
            </section>

            <!--
                Rappel du parcours : l'affectation se fait sur le plan,
                pas ici. Explicité une seule fois au niveau de la page
                plutôt que répété sur chaque carte.
            -->

            <p class="rappel-parcours">
                Pour affecter un équipement en stock, utilisez le
                glisser-déposer sur le
                <router-link to="/localisation">
                    plan de localisation
                </router-link>.
            </p>

            <!-- Filtres -->

            <Filters
                :filters="filtres"
                :initial-filters="filtresSelectionnes"
                @change="appliquerFiltres"
                @reset="reinitialiserFiltres"
            />

            <!-- Aucun équipement -->

            <EmptyState
                v-if="equipementsStock.length === 0"
                titre="Aucun équipement en stock"
                message="Le parc ne comporte aucun équipement en attente d'affectation. Les transferts vers le stock sont effectués depuis le plan de localisation."
            >
                <router-link
                    to="/localisation"
                    class="btn-secondary btn-sm"
                >
                    Ouvrir le plan de localisation
                </router-link>
            </EmptyState>

            <!-- Aucun résultat après filtrage -->

            <EmptyState
                v-else-if="equipementsVisibles.length === 0"
                titre="Aucun équipement ne correspond"
                message="Aucun équipement du stock ne correspond au filtre sélectionné."
            />

            <!-- Liste du stock -->

            <template v-else>
                <p class="resultats-compte">
                    <span class="resultats-compte__valeur">
                        {{ equipementsVisibles.length }}
                    </span>
                    équipement{{ equipementsVisibles.length > 1 ? 's' : '' }}
                    <template v-if="equipementsVisibles.length < equipementsStock.length">
                        sur {{ equipementsStock.length }}
                    </template>
                </p>

                <ul class="grille-cartes stock-liste">
                    <li
                        v-for="equipement in equipementsVisibles"
                        :key="equipement.id"
                    >
                        <article class="carte stock-carte">
                            <div class="carte__entete">
                                <h2 class="carte__titre">
                                    {{ equipement.nom }}
                                </h2>

                                <span
                                    class="badge-etat"
                                    :class="classeEtat(equipement.etat)"
                                >
                                    {{ afficherEtat(equipement.etat) }}
                                </span>
                            </div>

                            <dl class="stock-carte__faits">
                                <div class="stock-carte__fait">
                                    <dt>N° inventaire</dt>
                                    <dd class="mono">
                                        {{ equipement.numero_inventaire }}
                                    </dd>
                                </div>

                                <div class="stock-carte__fait">
                                    <dt>Type</dt>
                                    <dd>
                                        {{ afficherType(equipement.type) }}
                                    </dd>
                                </div>

                                <!--
                                    La condition de stock est
                                    renseignée par l'API pour tout
                                    matériel en stock.
                                -->
                                <div class="stock-carte__fait">
                                    <dt>Condition</dt>
                                    <dd>
                                        {{
                                            afficherCondition(equipement.condition_stock)
                                        }}
                                    </dd>
                                </div>
                            </dl>

                            <div class="carte__actions">
                                <router-link
                                    :to="`/equipements/${equipement.id}`"
                                    class="btn-ghost btn-sm"
                                >
                                    Voir la fiche
                                </router-link>

                                <!--
                                    Clôture de maintenance : action
                                    distincte de toute suppression ou
                                    d'un transfert. Elle ne vaut que
                                    pour un matériel effectivement en
                                    maintenance, comme l'exige l'API.
                                -->
                                <button
                                    v-if="equipement.etat === 'EN_MAINTENANCE'"
                                    type="button"
                                    class="btn-edit btn-sm"
                                    :disabled="actionEnCours === equipement.id"
                                    @click="terminerMaintenanceEquipement(equipement)"
                                >
                                    {{
                                        actionEnCours === equipement.id
                                            ? 'Clôture…'
                                            : 'Terminer la maintenance'
                                    }}
                                </button>
                            </div>
                        </article>
                    </li>
                </ul>
            </template>
        </template>

    </div>
</template>

<script setup>
/**
 * Console de gestion du stock et de la maintenance.
 *
 * Cette page est complémentaire de `PlanViewer` : elle montre ce qui
 * est en stock et permet de clôturer une maintenance, tandis que le
 * placement sur le plan et l'affectation restent gérés par
 * `PlanViewer`. Aucune seconde logique d'affectation n'est introduite.
 *
 * La liste provient de l'API du tableau de bord, comme auparavant :
 * cette page filtre et affiche, elle ne modifie pas le comportement
 * d'écriture. `terminerMaintenance` reste l'unique action.
 */
import { ref, computed, onMounted } from "vue";

import { getEquipementsDashboard } from "../services/dashboardService";
import { terminerMaintenance } from "../services/stockService";

import { useNotificationStore } from "../stores/notifications";

import AppAlert from "../components/AppAlert.vue";
import EmptyState from "../components/EmptyState.vue";
import Filters from "../components/Filters.vue";
import LoadingState from "../components/LoadingState.vue";

const notificationStore = useNotificationStore();

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

const filtresSelectionnes = ref({ etat: "" });

// --------------------------------------------------
// Équipements en stock
// --------------------------------------------------

const equipementsStock = computed(() => {
    return equipements.value.filter(
        (equipement) => equipement.situation === "EN_STOCK"
    );
});

/*
 * Filtrage d'affichage. Il porte sur la liste déjà chargée : aucun
 * appel supplémentaire n'est déclenché et le stock n'est pas
 * revalidé auprès du serveur.
 */
const equipementsVisibles = computed(() => {
    const etat = filtresSelectionnes.value.etat;

    if (!etat) {
        return equipementsStock.value;
    }

    return equipementsStock.value.filter(
        (equipement) => equipement.etat === etat
    );
});

const filtres = [
    {
        key: "etat",
        label: "État",
        type: "select",
        options: [
            { value: "EN_SERVICE", label: "En service" },
            { value: "EN_MAINTENANCE", label: "En maintenance" },
            { value: "EN_PANNE", label: "En panne" },
            { value: "HORS_SERVICE", label: "Hors service" },
        ],
    },
];

function appliquerFiltres(valeurs) {
    filtresSelectionnes.value = { ...valeurs };
}

function reinitialiserFiltres() {
    filtresSelectionnes.value = { etat: "" };
}

// --------------------------------------------------
// Statistiques
// --------------------------------------------------

const nombreEnMaintenance = computed(() => {
    return equipementsStock.value.filter(
        (equipement) => equipement.etat === "EN_MAINTENANCE"
    ).length;
});

const nombrePrets = computed(() => {
    return equipementsStock.value.filter(
        (equipement) => equipement.etat === "EN_SERVICE"
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

        errorMessage.value = "Impossible de charger les données du stock.";

    } finally {
        loading.value = false;
    }
}

// --------------------------------------------------
// Terminer la maintenance
// --------------------------------------------------

async function terminerMaintenanceEquipement(equipement) {
    actionEnCours.value = equipement.id;
    errorMessage.value = "";

    try {
        await terminerMaintenance(equipement.id);

        notificationStore.success(
            `Maintenance de « ${equipement.nom} » terminée. L'équipement est de nouveau en service.`
        );

        // Recharger les données
        await chargerDonnees();

    } catch (error) {
        console.error(error);

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de terminer la maintenance.";

        notificationStore.error(errorMessage.value);

    } finally {
        actionEnCours.value = null;
    }
}

// --------------------------------------------------
// Affichage conditionnel
// --------------------------------------------------

/*
 * Libellés lisibles des champs techniques.
 *
 * Ces tables reprennent les choix déclarés par le modèle Django. Une
 * valeur inconnue reste affichée telle quelle plutôt que masquée.
 */
const LIBELLES_TYPE = {
    ORDINATEUR: "Ordinateur",
};

const LIBELLES_CONDITION_STOCK = {
    NEUF: "Neuf",
    OCCASION: "Occasion",
    RECONDITIONNE: "Reconditionné",
};

const LIBELLES_ETAT = {
    EN_SERVICE: "En service",
    EN_MAINTENANCE: "En maintenance",
    EN_PANNE: "En panne",
    HORS_SERVICE: "Hors service",
};

/**
 * Traduit le code du type d'équipement renvoyé par l'API.
 *
 * Le modèle Equipement expose le type dans le champ "type" :
 * c'est ce champ qui est lu ici.
 */
function afficherType(type) {
    return LIBELLES_TYPE[type] || type || "—";
}

function afficherCondition(condition) {
    return LIBELLES_CONDITION_STOCK[condition] || condition || "—";
}

function afficherEtat(etat) {
    return LIBELLES_ETAT[etat] || etat || "—";
}

/*
 * La classe reprend la valeur brute de l'état : elle correspond aux
 * sélecteurs `etat-*` du design system, qui portent la couleur.
 *
 * Un état absent ne produit pas une classe `etat-` sans
 * signification : le badge reste alors neutre, et le libellé affiche
 * un tiret.
 */
function classeEtat(etat) {
    if (!etat) {
        return "";
    }

    return `etat-${String(etat).toLowerCase()}`;
}

onMounted(() => {
    chargerDonnees();
});
</script>

<style scoped>
.stock-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.rappel-parcours {
    margin: 0;
    padding: 0.65rem 0.85rem;
    background-color: var(--info-light);
    border: 1px solid var(--info-border);
    border-radius: var(--radius-md);
    color: var(--info-text);
    font-size: 0.875rem;
}

/* Une carte de stock occupe toute la cellule de la grille. */
.stock-liste > li {
    display: flex;
}

.stock-carte {
    width: 100%;
}

.stock-carte__faits {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.6rem 1rem;
    margin: 0;
}

.stock-carte__fait {
    min-width: 0;
}

.stock-carte__fait dt {
    color: var(--text-light);
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.stock-carte__fait dd {
    margin: 0.15rem 0 0;
    color: var(--text-main);
    font-size: 0.875rem;
    font-weight: 500;
    word-break: break-word;
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}

@media (max-width: 640px) {
    .statistiques {
        grid-template-columns: 1fr 1fr;
    }
}
</style>
