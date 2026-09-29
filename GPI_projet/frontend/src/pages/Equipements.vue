<template>
    <div class="page-container equipements-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Équipements
                </h1>

                <p class="page-heading__subtitle">
                    <template v-if="estAdmin">
                        Gestion du parc informatique
                    </template>

                    <template v-else>
                        Consultation du parc informatique en lecture seule
                    </template>
                </p>
            </div>

            <div class="page-heading__actions">
                <button
                    v-if="estAdmin"
                    type="button"
                    class="btn-primary"
                    @click="ouvrirCreation"
                >
                    Nouvel équipement
                </button>
            </div>
        </div>

        <!-- Recherche et filtres -->

        <Filters
            :filters="filtresActifs"
            :initial-filters="filters"
            @change="setFilters"
            @reset="resetFilters"
        />

        <!-- Erreur -->

        <AppAlert
            v-if="errorMessage"
            type="error"
            :message="errorMessage"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="loading"
            titre="Chargement des équipements…"
        />

        <!-- Aucun résultat -->

        <EmptyState
            v-else-if="!errorMessage && filteredItems.length === 0"
            :titre="titreAucunResultat"
            :message="messageAucunResultat"
        >
            <button
                v-if="estAdmin && aucunEquipement"
                type="button"
                class="btn-primary btn-sm"
                @click="ouvrirCreation"
            >
                Créer le premier équipement
            </button>
        </EmptyState>

        <!-- Résultats -->

        <template v-else-if="!loading && !errorMessage">
            <div class="resultats-barre">
                <p class="resultats-compte">
                    <span class="resultats-compte__valeur">
                        {{ filteredItems.length }}
                    </span>
                    équipement{{ filteredItems.length > 1 ? 's' : '' }}
                    affiché{{ filteredItems.length > 1 ? 's' : '' }}
                    <template v-if="filtresReprises.length">
                        sur {{ equipements.length }}
                    </template>
                </p>

                <!--
                    Rappel des filtres actifs : sans lui, un résultat
                    restreint est indiscernable d'un parc réduit.
                -->
                <p
                    v-if="filtresReprises.length"
                    class="resultats-rappel"
                >
                    <span class="resultats-rappel__intitule">
                        Filtres :
                    </span>

                    <span
                        v-for="filtre in filtresReprises"
                        :key="filtre.cle"
                        class="marque-filtre"
                    >
                        <span class="marque-filtre__cle">
                            {{ filtre.label }}
                        </span>

                        <span class="marque-filtre__valeur">
                            {{ filtre.valeur }}
                        </span>
                    </span>
                </p>
            </div>

            <div class="table-scroll">
                <!-- Vue administrateur -->

                <table v-if="estAdmin">
                    <caption class="visually-hidden">
                        Liste des équipements du parc, avec les
                        informations techniques réservées à l'administration
                    </caption>

                    <thead>
                        <tr>
                            <th scope="col">ID</th>

                            <TableSort
                                column-key="nom"
                                label="Nom"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="type"
                                label="Type"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="numero_inventaire"
                                label="N° inventaire"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="fabricant"
                                label="Fabricant"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="modele"
                                label="Modèle"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="numero_serie"
                                label="N° série"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="adresse_ip"
                                label="Adresse IP"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="adresse_mac"
                                label="Adresse MAC"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="etat"
                                label="État"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <TableSort
                                column-key="situation"
                                label="Situation"
                                :current-sort-key="sortKey"
                                :current-sort-order="sortOrder"
                                @sort="setSort"
                            />

                            <th scope="col">Actions</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr
                            v-for="equipement in paginatedItems"
                            :key="equipement.id"
                        >
                            <td class="cellule-id">
                                {{ equipement.id }}
                            </td>

                            <td>
                                <router-link
                                    class="lien-cellule"
                                    :to="`/equipements/${equipement.id}`"
                                >
                                    {{ equipement.nom }}
                                </router-link>
                            </td>

                            <td>{{ libelleType(equipement.type) }}</td>
                            <td class="cellule-mono">
                                {{ equipement.numero_inventaire }}
                            </td>
                            <td>{{ equipement.fabricant || "—" }}</td>
                            <td>{{ equipement.modele || "—" }}</td>

                            <td class="cellule-mono">
                                {{ equipement.numero_serie || "—" }}
                            </td>

                            <td class="cellule-mono">
                                {{ equipement.adresse_ip || "—" }}
                            </td>

                            <td class="cellule-mono">
                                {{ equipement.adresse_mac || "—" }}
                            </td>

                            <td>
                                <span
                                    class="badge-etat"
                                    :class="`etat-${equipement.etat.toLowerCase()}`"
                                >
                                    {{ libelleEtat(equipement.etat) }}
                                </span>
                            </td>

                            <td>
                                <span
                                    class="badge-situation"
                                    :class="`situation-${equipement.situation.toLowerCase()}`"
                                >
                                    {{ libelleSituation(equipement.situation) }}
                                </span>
                            </td>

                            <td>
                                <div class="actions-cellule">
                                    <button
                                        type="button"
                                        class="btn-ghost btn-sm"
                                        :disabled="!equipement.salle"
                                        :title="
                                            equipement.salle
                                                ? 'Voir la position sur le plan'
                                                : 'Aucune salle attribuée'
                                        "
                                        @click="voirSurPlan(equipement)"
                                    >
                                        <span aria-hidden="true">◈</span>
                                        Plan
                                    </button>

                                    <button
                                        type="button"
                                        class="btn-edit btn-sm"
                                        @click="ouvrirModification(equipement)"
                                    >
                                        Modifier
                                    </button>

                                    <button
                                        type="button"
                                        class="btn-delete btn-sm"
                                        @click="demanderSuppression(equipement)"
                                    >
                                        Supprimer
                                    </button>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>

                <!-- Vue visiteur -->

                <table v-else>
                    <caption class="visually-hidden">
                        Liste des équipements du parc informatique
                    </caption>

                    <thead>
                        <tr>
                            <th scope="col">Équipement</th>
                            <th scope="col">Type</th>
                            <th scope="col">N° inventaire</th>
                            <th scope="col">Salle</th>
                            <th scope="col">État</th>
                            <th scope="col">Plan</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr
                            v-for="equipement in paginatedItems"
                            :key="equipement.id"
                        >
                            <td>
                                <router-link
                                    class="lien-cellule"
                                    :to="`/equipements/${equipement.id}`"
                                >
                                    {{ equipement.nom }}
                                </router-link>
                            </td>

                            <td>{{ libelleType(equipement.type) }}</td>
                            <td class="cellule-mono">
                                {{ equipement.numero_inventaire }}
                            </td>
                            <td>{{ nomSalle(equipement.salle) }}</td>

                            <td>
                                <span
                                    class="badge-etat"
                                    :class="`etat-${equipement.etat.toLowerCase()}`"
                                >
                                    {{ libelleEtat(equipement.etat) }}
                                </span>
                            </td>

                            <td>
                                <button
                                    v-if="equipement.salle"
                                    type="button"
                                    class="btn-ghost btn-sm"
                                    @click="voirSurPlan(equipement)"
                                >
                                    <span aria-hidden="true">◈</span>
                                    Voir sur le plan
                                </button>

                                <span
                                    v-else
                                    class="text-muted"
                                >
                                    Non positionné
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <Pagination
                :current-page="currentPage"
                :page-size="pageSize"
                :total-items="filteredItems.length"
                @change="setPage"
                @page-size-change="setPageSize"
            />
        </template>

        <!-- Formulaire (administration uniquement) -->

        <EquipementForm
            v-if="afficherFormulaire && estAdmin"
            :mode="modeFormulaire"
            :equipement="equipementSelectionne"
            :chargement="saving"
            :erreurs="erreursChamps"
            @close="fermerFormulaire"
            @save="enregistrer"
        />

        <!-- Confirmation de suppression -->

        <ConfirmDialog
            v-if="equipementASupprimer && estAdmin"
            titre="Supprimer cet équipement ?"
            :message="`L'équipement « ${equipementASupprimer.nom} » sera définitivement supprimé du parc.`"
            consequence="Cette action est irréversible. L'historique des signalements associés à cet équipement sera également perdu."
            @confirm="supprimer"
            @cancel="equipementASupprimer = null"
        />

    </div>
</template>

<script setup>
/**
 * Liste des équipements, en administration comme en consultation.
 *
 * La séparation des deux vues est portée par le serializer : un
 * visiteur ne reçoit ni numéro de série, ni adresse IP, ni adresse
 * MAC. Ces colonnes n'existent que dans le tableau administrateur.
 *
 * La logique métier reste celle du service et du composable de table :
 * cette page organise l'affichage, la pagination et le tri.
 */
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';

import {
    getEquipements,
    creerEquipement,
    modifierEquipement,
    supprimerEquipement
} from '../services/equipementService';
import { getSalles } from '../services/salleService';

import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notifications';
import { useTableData } from '../composables/useTableData';

import AppAlert from '../components/AppAlert.vue';
import ConfirmDialog from '../components/ConfirmDialog.vue';
import EmptyState from '../components/EmptyState.vue';
import EquipementForm from '../components/EquipementForm.vue';
import Filters from '../components/Filters.vue';
import LoadingState from '../components/LoadingState.vue';
import Pagination from '../components/Pagination.vue';
import TableSort from '../components/TableSort.vue';

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const equipements = ref([]);
const salles = ref([]);
const loading = ref(false);
const saving = ref(false);
const errorMessage = ref("");
const erreursChamps = ref({});

const afficherFormulaire = ref(false);
const modeFormulaire = ref("creation");
const equipementSelectionne = ref(null);
const equipementASupprimer = ref(null);

const estAdmin = computed(() => authStore.isAdmin);

/*
 * Libellés lisibles des champs techniques.
 *
 * La classe CSS conserve la valeur brute (contraste visuel) tandis
 * que le texte affiché reste compréhensible. L'information n'est donc
 * jamais portée par la couleur seule.
 *
 * Ces tables reprennent les choix déclarés par le modèle Django. Une
 * valeur inconnue reste affichée telle quelle plutôt que masquée.
 */
const LIBELLES_TYPE = {
    ORDINATEUR: "Ordinateur",
};

const LIBELLES_ETAT = {
    EN_SERVICE: "En service",
    EN_PANNE: "En panne",
    EN_MAINTENANCE: "En maintenance",
    HORS_SERVICE: "Hors service",
};

const LIBELLES_SITUATION = {
    AFFECTE: "Affecté",
    EN_STOCK: "En stock",
};

function libelleType(type) {
    return LIBELLES_TYPE[type] || type || "—";
}

function libelleEtat(etat) {
    return LIBELLES_ETAT[etat] || etat || "—";
}

function libelleSituation(situation) {
    return LIBELLES_SITUATION[situation] || situation || "—";
}

/*
 * L'API renvoie `salle` sous forme d'identifiant (et non d'objet).
 * On le traduit ici en nom affichable.
 */
function nomSalle(salleId) {
    if (!salleId) {
        return "Non affecté";
    }

    const salle = salles.value.find(
        (item) => String(item.id) === String(salleId)
    );

    return salle ? salle.nom : `Salle ${salleId}`;
}

/*
 * Filtres.
 *
 * Le visiteur ne dispose que des champs réellement exposés par le
 * serializer public : ni adresse IP, ni adresse MAC, ni numéro de
 * série.
 */
const filtresVisiteur = [
    {
        key: 'nom',
        label: 'Recherche',
        type: 'text',
        placeholder: 'Nom ou numéro d’inventaire'
    },
    {
        key: 'type',
        label: 'Type',
        type: 'select',
        options: [
            { value: 'ORDINATEUR', label: 'Ordinateur' }
        ]
    },
    {
        key: 'situation',
        label: 'Situation',
        type: 'select',
        options: [
            { value: 'AFFECTE', label: 'Affecté' },
            { value: 'EN_STOCK', label: 'En stock' }
        ]
    }
];

const filtresAdministrateur = [
    ...filtresVisiteur,
    {
        key: 'etat',
        label: 'État',
        type: 'select',
        options: [
            { value: 'EN_SERVICE', label: 'En service' },
            { value: 'EN_PANNE', label: 'En panne' },
            { value: 'EN_MAINTENANCE', label: 'En maintenance' },
            { value: 'HORS_SERVICE', label: 'Hors service' }
        ]
    }
];

const filtresActifs = computed(() =>
    estAdmin.value ? filtresAdministrateur : filtresVisiteur
);

// Utilisation du composable pour pagination/filtrage/tri
const {
    currentPage,
    pageSize,
    sortKey,
    sortOrder,
    filters,
    filteredItems,
    paginatedItems,
    setPage,
    setPageSize,
    setSort,
    setFilters,
    resetFilters
} = useTableData(equipements, {
    defaultPageSize: 25,
    defaultSortKey: 'nom',
    defaultSortOrder: 'asc'
});

/*
 * Rappel des filtres actifs, avec leur libellé résolu : une valeur
 * brute telle que « EN_PANNE » ne serait pas lisible dans la barre de
 * résultats.
 */
const filtresReprises = computed(() => {
    const parCle = Object.fromEntries(
        filtresActifs.value.map((filtre) => [filtre.key, filtre])
    );

    return Object.entries(filters.value)
        .filter(([, valeur]) => String(valeur || '').trim() !== '')
        .map(([cle, valeur]) => {
            const definition = parCle[cle];
            const option = definition?.options?.find(
                (item) => item.value === valeur
            );

            return {
                cle,
                label: definition?.label || cle,
                valeur: option?.label || String(valeur),
            };
        });
});

const aucunEquipement = computed(
    () => equipements.value.length === 0
);

const titreAucunResultat = computed(() =>
    aucunEquipement.value
        ? "Aucun équipement enregistré"
        : "Aucun équipement trouvé"
);

const messageAucunResultat = computed(() => {
    if (aucunEquipement.value) {
        return "Le parc ne contient aucun équipement pour le moment.";
    }

    return Object.keys(filters.value).length > 0
        ? 'Aucun équipement ne correspond aux filtres sélectionnés.'
        : 'Aucun équipement à afficher.';
});

async function chargerEquipements() {
    loading.value = true;
    errorMessage.value = "";

    try {
        const [donneesEquipements, donneesSalles] = await Promise.all([
            getEquipements(),
            getSalles(),
        ]);

        equipements.value = donneesEquipements;
        salles.value = donneesSalles;

    } catch (error) {
        console.error(
            "Erreur lors du chargement des équipements :", error
        );

        errorMessage.value = "Impossible de charger les équipements.";

    } finally {
        loading.value = false;
    }
}

function ouvrirCreation() {
    modeFormulaire.value = "creation";
    equipementSelectionne.value = null;
    erreursChamps.value = {};
    afficherFormulaire.value = true;
}

function ouvrirModification(equipement) {
    modeFormulaire.value = "modification";
    equipementSelectionne.value = equipement;
    erreursChamps.value = {};
    afficherFormulaire.value = true;
}

function fermerFormulaire() {
    afficherFormulaire.value = false;
    equipementSelectionne.value = null;
    erreursChamps.value = {};
}

/*
 * Extrait les erreurs renvoyées par l'API.
 *
 * DRF répond soit par un objet `{ champ: [messages] }`, soit par une
 * liste, soit par `{ detail }`. Ces messages sont transmis au
 * formulaire tels quels : le backend reste l'autorité de la
 * validation, le frontend ne les réécrit pas.
 */
function extraireErreurs(error) {
    const donnees = error.response?.data;

    if (!donnees) {
        return {};
    }

    if (typeof donnees === "string") {
        return { detail: donnees };
    }

    if (Array.isArray(donnees)) {
        return { detail: donnees.join(" ") };
    }

    const champs = {};

    Object.entries(donnees).forEach(([champ, messages]) => {
        champs[champ] = Array.isArray(messages)
            ? messages.join(" ")
            : String(messages);
    });

    return champs;
}

function voirSurPlan(equipement) {
    router.push({
        path: '/plan',
        query: { equipementId: equipement.id }
    });
}

async function enregistrer(donnees) {
    saving.value = true;
    erreursChamps.value = {};

    try {
        if (modeFormulaire.value === "creation") {
            await creerEquipement(donnees);
            notificationStore.success("Équipement créé avec succès");

        } else {
            await modifierEquipement(equipementSelectionne.value.id, donnees);
            notificationStore.success("Équipement modifié avec succès");
        }

        fermerFormulaire();
        await chargerEquipements();

    } catch (error) {
        console.error("Erreur lors de l'enregistrement:", error);

        /*
         * L'API reste l'autorité de la validation : ses messages
         * sont affichés champ par champ plutôt que remplacés par un
         * texte générique qui masquerait la cause réelle.
         */
        erreursChamps.value = extraireErreurs(error);

        const errorMsg =
            erreursChamps.value.detail ||
            "Impossible d'enregistrer l'équipement.";

        errorMessage.value = errorMsg;
        notificationStore.error(errorMsg);

        // Le formulaire reste ouvert pour permettre la correction.

    } finally {
        saving.value = false;
    }
}

function demanderSuppression(equipement) {
    equipementASupprimer.value = equipement;
}

async function supprimer() {
    const equipement = equipementASupprimer.value;

    if (!equipement) {
        return;
    }

    try {
        await supprimerEquipement(equipement.id);

        equipementASupprimer.value = null;
        notificationStore.success("Équipement supprimé avec succès");
        await chargerEquipements();

    } catch (error) {
        console.error("Erreur lors de la suppression:", error);

        equipementASupprimer.value = null;

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de supprimer l'équipement.";

        notificationStore.error(errorMessage.value);
    }
}

onMounted(() => {
    chargerEquipements();
});
</script>

<style scoped>
.equipements-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.cellule-id {
    color: var(--text-light);
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}

/* Valeurs techniques : la chasse fixe aide à lire un identifiant
   ou une adresse sans confondre 0 et O, 1 et l. */
.cellule-mono {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
    color: var(--text-muted);
}

.lien-cellule {
    font-weight: 500;
    color: var(--primary);
}

.actions-cellule {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

@media (max-width: 640px) {
    .actions-cellule {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
