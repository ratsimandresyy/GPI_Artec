<template>
    <div class="page-container tickets-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Signalements
                </h1>

                <p class="page-heading__subtitle">
                    Pannes et réclamations déclarées sur le parc
                    informatique.
                </p>
            </div>

            <div class="page-heading__actions">
                <button
                    type="button"
                    class="btn-primary"
                    @click="ouvrirCreation"
                >
                    Nouveau signalement
                </button>
            </div>
        </div>

        <!-- Erreur -->

        <AppAlert
            v-if="erreur"
            type="error"
            :message="erreur"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="chargement"
            titre="Chargement des signalements…"
        />

        <template v-else-if="!erreur">
            <!--
                Résumé : les compteurs sont dérivés de la liste déjà
                chargée, à partir des valeurs réellement fournies par
                l'API. Aucun appel statistique supplémentaire.
            -->

            <section
                class="statistiques"
                aria-label="Situation des signalements"
            >
                <div class="statistique">
                    <span class="statistique__intitule">
                        Total
                    </span>

                    <span class="statistique__valeur">
                        {{ tickets.length }}
                    </span>
                </div>

                <div class="statistique">
                    <span class="statistique__intitule">
                        Ouverts
                    </span>

                    <span class="statistique__valeur">
                        {{ nombreParStatut.OUVERT || 0 }}
                    </span>
                </div>

                <div
                    class="statistique"
                    :class="{ 'statistique--alerte': (nombreParStatut.EN_COURS || 0) > 0 }"
                >
                    <span class="statistique__intitule">
                        En cours
                    </span>

                    <span class="statistique__valeur">
                        {{ nombreParStatut.EN_COURS || 0 }}
                    </span>
                </div>

                <div class="statistique">
                    <span class="statistique__intitule">
                        Résolus
                    </span>

                    <span class="statistique__valeur">
                        {{ nombreParStatut.RESOLU || 0 }}
                    </span>
                </div>

                <div
                    v-if="nombreCritiques > 0"
                    class="statistique statistique--alerte"
                >
                    <span class="statistique__intitule">
                        Priorité critique
                    </span>

                    <span class="statistique__valeur">
                        {{ nombreCritiques }}
                    </span>
                </div>
            </section>

            <!-- Recherche et filtres -->

            <Filters
                :filters="filtres"
                :initial-filters="filtresActifs"
                @change="setFilters"
                @reset="resetFilters"
            />

            <!-- Aucun signalement -->

            <EmptyState
                v-if="tickets.length === 0"
                titre="Aucun signalement enregistré"
                message="Aucun équipement n'a fait l'objet d'une déclaration de panne ou de réclamation."
            />

            <!-- Aucun résultat après filtrage -->

            <EmptyState
                v-else-if="filteredItems.length === 0"
                titre="Aucun signalement ne correspond"
                message="Aucun signalement ne correspond aux critères sélectionnés."
            />

            <!-- Liste -->

            <template v-else>
                <div class="resultats-barre">
                    <p class="resultats-compte">
                        <span class="resultats-compte__valeur">
                            {{ filteredItems.length }}
                        </span>
                        signalement{{ filteredItems.length > 1 ? 's' : '' }}
                        <template v-if="filteredItems.length < tickets.length">
                            sur {{ tickets.length }}
                        </template>
                    </p>
                </div>

                <div class="table-scroll">
                    <table>
                        <caption class="visually-hidden">
                            Signalements de panne et de réclamation
                        </caption>

                        <thead>
                            <tr>
                                <th scope="col">N°</th>

                                <TableSort
                                    column-key="titre"
                                    label="Titre"
                                    :current-sort-key="sortKey"
                                    :current-sort-order="sortOrder"
                                    @sort="setSort"
                                />

                                <TableSort
                                    column-key="equipement_nom"
                                    label="Équipement"
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
                                    column-key="statut"
                                    label="Statut"
                                    :current-sort-key="sortKey"
                                    :current-sort-order="sortOrder"
                                    @sort="setSort"
                                />

                                <TableSort
                                    column-key="priorite"
                                    label="Priorité"
                                    :current-sort-key="sortKey"
                                    :current-sort-order="sortOrder"
                                    @sort="setSort"
                                />

                                <TableSort
                                    column-key="date_signalement"
                                    label="Déclaré le"
                                    :current-sort-key="sortKey"
                                    :current-sort-order="sortOrder"
                                    @sort="setSort"
                                />

                                <th scope="col">Résolu le</th>

                                <th scope="col">Actions</th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr
                                v-for="ticket in paginatedItems"
                                :key="ticket.id"
                            >
                                <td class="cellule-id">
                                    #{{ ticket.id }}
                                </td>

                                <td>
                                    <span class="ticket-titre">
                                        {{ ticket.titre }}
                                    </span>

                                    <span class="ticket-equipement">
                                        N° inventaire
                                        {{ ticket.numero_inventaire }}
                                    </span>
                                </td>

                                <td>
                                    {{ ticket.equipement_nom }}
                                </td>

                                <td>
                                    <span
                                        class="type-signalement"
                                        :class="`type-${ticket.type.toLowerCase()}`"
                                    >
                                        {{ libelleType(ticket.type) }}
                                    </span>
                                </td>

                                <td>
                                    <span
                                        class="statut"
                                        :class="`statut-${ticket.statut.toLowerCase()}`"
                                    >
                                        {{ libelleStatut(ticket.statut) }}
                                    </span>
                                </td>

                                <td>
                                    <span
                                        class="priorite"
                                        :class="`priorite-${ticket.priorite.toLowerCase()}`"
                                    >
                                        {{ libellePriorite(ticket.priorite) }}
                                    </span>
                                </td>

                                <td class="cellule-date">
                                    {{ formaterDate(ticket.date_signalement) }}
                                </td>

                                <td class="cellule-date">
                                    {{ formaterDate(ticket.date_resolution) }}
                                </td>

                                <!--
                                    Les actions d'administration sont
                                    présentée dans leur propre colonne :
                                    consulter, prendre en charge,
                                    résoudre et qualifier restent
                                    distincts.
                                -->
                                <td>
                                    <div
                                        v-if="estAdmin"
                                        class="actions-cellule"
                                    >
                                        <button
                                            v-if="ticket.statut === 'OUVERT'"
                                            type="button"
                                            class="btn-edit btn-sm"
                                            :disabled="priseEnChargeEnCours === ticket.id"
                                            @click="prendreEnCharge(ticket)"
                                        >
                                            {{
                                                priseEnChargeEnCours === ticket.id
                                                    ? 'Prise en charge…'
                                                    : 'Prendre en charge'
                                            }}
                                        </button>

                                        <button
                                            v-if="ticket.statut === 'EN_COURS'"
                                            type="button"
                                            class="btn-primary btn-sm"
                                            :disabled="resolutionEnCours === ticket.id"
                                            @click="ouvrirResolution(ticket)"
                                        >
                                            {{
                                                resolutionEnCours === ticket.id
                                                    ? 'Résolution…'
                                                    : 'Résoudre'
                                            }}
                                        </button>

                                        <button
                                            v-if="ticket.statut !== 'RESOLU'"
                                            type="button"
                                            class="btn-secondary btn-sm"
                                            :disabled="qualificationEnCours === ticket.id"
                                            @click="ouvrirQualification(ticket)"
                                        >
                                            {{
                                                qualificationEnCours === ticket.id
                                                    ? 'Qualification…'
                                                    : 'Qualifier'
                                            }}
                                        </button>

                                        <span
                                            v-if="ticket.statut === 'RESOLU'"
                                            class="text-muted"
                                        >
                                            Aucune action
                                        </span>
                                    </div>

                                    <span
                                        v-else
                                        class="text-muted"
                                    >
                                        —
                                    </span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <!--
                    Erreur d'action rattachée au signalement concerné :
                    elle ne doit pas s'afficher sur les autres lignes.
                -->
                <AppAlert
                    v-if="erreurAction"
                    type="error"
                    :message="`Signalement #${ticketEnErreur} — ${erreurAction}`"
                />

                <Pagination
                    :current-page="currentPage"
                    :page-size="pageSize"
                    :total-items="filteredItems.length"
                    @change="setPage"
                    @page-size-change="setPageSize"
                />
            </template>
        </template>

        <!-- Formulaire de création -->

        <section
            v-if="afficherFormulaire"
            class="formulaire"
            aria-labelledby="titre-formulaire-ticket"
        >
            <h2
                id="titre-formulaire-ticket"
                class="formulaire__titre"
            >
                Nouveau signalement
            </h2>

            <p class="formulaire__legende">
                Déclarez une panne ou une réclamation sur un équipement
                affecté.
            </p>

            <AppAlert
                v-if="erreurCreation"
                type="error"
                :message="erreurCreation"
            />

            <form @submit.prevent="enregistrerTicket">
                <div class="formulaire__groupe">
                    <p class="formulaire__groupe-titre">
                        Signalement
                    </p>

                    <div class="form-group">
                        <label for="ticket-equipement">
                            Équipement
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <select
                            id="ticket-equipement"
                            v-model="equipementSelectionne"
                            :disabled="chargementEquipements || creationEnCours"
                        >
                            <option value="">
                                Sélectionner un équipement
                            </option>

                            <option
                                v-for="equipement in equipements"
                                :key="equipement.id"
                                :value="equipement.id"
                            >
                                {{ equipement.nom }} — {{ equipement.numero_inventaire }}
                            </option>
                        </select>

                        <p class="champ-aide">
                            Seuls les équipements affectés à une salle
                            peuvent faire l'objet d'un signalement.
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="ticket-titre">
                            Titre
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <input
                            id="ticket-titre"
                            v-model="titre"
                            type="text"
                            :disabled="creationEnCours"
                            placeholder="Titre du signalement…"
                        >
                    </div>

                    <div class="form-group">
                        <label for="ticket-type">
                            Nature
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <select
                            id="ticket-type"
                            v-model="type"
                            :disabled="creationEnCours"
                        >
                            <option value="MAINTENANCE">Maintenance</option>
                            <option value="RECLAMATION">Réclamation</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="ticket-priorite">
                            Urgence
                        </label>

                        <select
                            id="ticket-priorite"
                            v-model="priorite"
                            :disabled="creationEnCours"
                        >
                            <option value="BASSE">Basse</option>
                            <option value="NORMALE">Normale</option>
                            <option value="HAUTE">Haute</option>
                        </select>

                        <p class="champ-aide">
                            La priorité critique ne peut pas être choisie
                            à la création : elle est réservée à la
                            qualification d'un ticket déjà enregistré.
                        </p>
                    </div>
                </div>

                <div class="formulaire__groupe">
                    <p class="formulaire__groupe-titre">
                        Description
                    </p>

                    <div class="form-group">
                        <label for="ticket-description">
                            Description
                            <span
                                class="requis"
                                aria-hidden="true"
                            >*</span>
                        </label>

                        <textarea
                            id="ticket-description"
                            v-model="description"
                            rows="5"
                            :disabled="creationEnCours"
                            placeholder="Décrivez la panne ou la réclamation…"
                        ></textarea>
                    </div>
                </div>

                <div class="formulaire__actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        :disabled="creationEnCours"
                        @click="fermerFormulaire"
                    >
                        Annuler
                    </button>

                    <button
                        type="submit"
                        class="btn-primary"
                        :disabled="creationEnCours"
                    >
                        {{ creationEnCours ? "Création…" : "Créer le signalement" }}
                    </button>
                </div>
            </form>
        </section>

        <!-- Modale de résolution -->

        <div
            v-if="afficherModalResolution"
            class="modal-overlay"
            @click.self="fermerModalResolution"
        >
            <div
                class="modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="titre-resolution"
            >
                <h2
                    id="titre-resolution"
                    class="formulaire__titre"
                >
                    Résoudre le signalement
                </h2>

                <p
                    v-if="ticketEnResolution"
                    class="modal__contexte"
                >
                    #{{ ticketEnResolution.id }} — {{ ticketEnResolution.titre }}
                </p>

                <div class="form-group">
                    <label for="ticket-commentaire">
                        Commentaire de résolution
                        <span
                            class="requis"
                            aria-hidden="true"
                        >*</span>
                    </label>

                    <textarea
                        id="ticket-commentaire"
                        v-model="commentaireResolution"
                        rows="5"
                        :disabled="resolutionEnCours"
                        placeholder="Décrivez la résolution…"
                    ></textarea>
                </div>

                <!--
                    Diagramme d'activité « Matériel réparé ? » :
                    oui, le matériel est remis en service à la
                    clôture ; non, il reste hors service.
                -->
                <fieldset class="formulaire__groupe">
                    <legend class="formulaire__groupe-titre">
                        Matériel réparé ?
                    </legend>

                    <label class="choix">
                        <input
                            v-model="materielRepare"
                            type="radio"
                            :value="true"
                            :disabled="resolutionEnCours"
                        >
                        Oui, remettre le matériel en service
                    </label>

                    <label class="choix">
                        <input
                            v-model="materielRepare"
                            type="radio"
                            :value="false"
                            :disabled="resolutionEnCours"
                        >
                        Non, maintenir le matériel hors service
                    </label>
                </fieldset>

                <AppAlert
                    v-if="erreurResolution"
                    type="error"
                    :message="erreurResolution"
                />

                <div class="formulaire__actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        :disabled="resolutionEnCours"
                        @click="fermerModalResolution"
                    >
                        Annuler
                    </button>

                    <button
                        type="button"
                        class="btn-primary"
                        :disabled="resolutionEnCours"
                        @click="confirmerResolution"
                    >
                        {{ resolutionEnCours ? "Résolution…" : "Résoudre" }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Modale de qualification -->

        <div
            v-if="afficherModalQualification"
            class="modal-overlay"
            @click.self="fermerModalQualification"
        >
            <div
                class="modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="titre-qualification"
            >
                <h2
                    id="titre-qualification"
                    class="formulaire__titre"
                >
                    Qualifier le signalement
                </h2>

                <p
                    v-if="ticketEnQualification"
                    class="modal__contexte"
                >
                    #{{ ticketEnQualification.id }} — {{ ticketEnQualification.titre }}
                </p>

                <p class="formulaire__legende">
                    La qualification fixe la nature exacte du signalement
                    et son niveau d'urgence réel.
                </p>

                <div class="form-group">
                    <label for="qualification-type">
                        Nature
                    </label>

                    <select
                        id="qualification-type"
                        v-model="typeQualification"
                        :disabled="qualificationEnCours"
                    >
                        <option value="MAINTENANCE">Maintenance</option>
                        <option value="RECLAMATION">Réclamation</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="qualification-priorite">
                        Priorité
                    </label>

                    <select
                        id="qualification-priorite"
                        v-model="prioriteQualification"
                        :disabled="qualificationEnCours"
                    >
                        <option value="BASSE">Basse</option>
                        <option value="NORMALE">Normale</option>
                        <option value="HAUTE">Haute</option>
                        <option value="CRITIQUE">Critique</option>
                    </select>
                </div>

                <AppAlert
                    v-if="erreurQualification"
                    type="error"
                    :message="erreurQualification"
                />

                <div class="formulaire__actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        :disabled="qualificationEnCours"
                        @click="fermerModalQualification"
                    >
                        Annuler
                    </button>

                    <button
                        type="button"
                        class="btn-primary"
                        :disabled="qualificationEnCours"
                        @click="confirmerQualification"
                    >
                        {{ qualificationEnCours ? "Qualification…" : "Qualifier" }}
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>

<script setup>
/**
 * Suivi des signalements de panne et de réclamation.
 *
 * `TicketPanne` couvre deux natures de déclaration, la panne et la
 * réclamation. Il ne s'agit pas d'un système général de gestion de
 * tickets : aucune catégorie, aucun workflow et aucun champ
 * supplémentaire ne sont introduits ici.
 *
 * Les priorités existent bien côté API ; la formulation du formulaire
 * de création s'en tient aux trois niveaux que l'administration est
 * censée qualifier, la priorité critique restant son apanage via la
 * qualification. Le tableau, lui, affiche la valeur réelle.
 *
 * Tous les appels d'API sont conservés à l'identique.
 */
import { ref, computed, onMounted, onBeforeUnmount } from "vue";

import {
    getTickets,
    creerTicket,
    prendreEnChargeTicket,
    resoudreTicket,
    qualifierTicket,
} from "../services/ticketService";

import { getEquipementsDashboard } from "../services/dashboardService";

import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";
import { useTableData } from "../composables/useTableData";

import AppAlert from "../components/AppAlert.vue";
import EmptyState from "../components/EmptyState.vue";
import Filters from "../components/Filters.vue";
import LoadingState from "../components/LoadingState.vue";
import Pagination from "../components/Pagination.vue";
import TableSort from "../components/TableSort.vue";

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const tickets = ref([]);
const chargement = ref(false);
const erreur = ref("");

const afficherFormulaire = ref(false);

const equipements = ref([]);
const chargementEquipements = ref(false);

const equipementSelectionne = ref("");
const titre = ref("");
const type = ref("MAINTENANCE");
const priorite = ref("NORMALE");
const description = ref("");

const creationEnCours = ref(false);
const erreurCreation = ref("");

const priseEnChargeEnCours = ref(null);
const resolutionEnCours = ref(null);
const qualificationEnCours = ref(null);

/*
 * Chaque action porte sa propre erreur : une défaillance sur un
 * signalement ne doit pas être affichée sur tous les autres.
 */
const erreurAction = ref("");
const ticketEnErreur = ref(null);
const erreurResolution = ref("");
const erreurQualification = ref("");

const ticketEnResolution = ref(null);
const commentaireResolution = ref("");
const afficherModalResolution = ref(false);

// « Materiel repare ? » du diagramme d'activite : par oui, le matériel
// est remis en service a la cloture.
const materielRepare = ref(true);

const ticketEnQualification = ref(null);
const typeQualification = ref("MAINTENANCE");
const prioriteQualification = ref("NORMALE");
const afficherModalQualification = ref(false);

const estAdmin = computed(() => authStore.isAdmin);

/*
 * Compteurs de situation, dérivés de la liste déjà chargée. Le
 * compteur CRITIQUE compte les signalements de priorité critique, pas
 * un statut : les deux notions sont comptées séparément.
 */
const nombreParStatut = computed(() => {
    const compte = {};

    tickets.value.forEach((ticket) => {
        compte[ticket.statut] = (compte[ticket.statut] || 0) + 1;
    });

    return compte;
});

const nombreCritiques = computed(
    () => tickets.value.filter(
        (ticket) => ticket.priorite === "CRITIQUE"
    ).length
);

/*
 * Les filtres s'appuient sur les champs réellement présents dans la
 * réponse de l'API.
 */
const filtres = [
    {
        key: "titre",
        label: "Recherche",
        type: "text",
        placeholder: "Titre du signalement",
    },
    {
        key: "equipement_nom",
        label: "Équipement",
        type: "text",
        placeholder: "Nom de l'équipement",
    },
    {
        key: "type",
        label: "Nature",
        type: "select",
        options: [
            { value: "MAINTENANCE", label: "Maintenance" },
            { value: "RECLAMATION", label: "Réclamation" },
        ],
    },
    {
        key: "statut",
        label: "Statut",
        type: "select",
        options: [
            { value: "OUVERT", label: "Ouvert" },
            { value: "EN_COURS", label: "En cours" },
            { value: "RESOLU", label: "Résolu" },
            { value: "ANNULE", label: "Annulé" },
        ],
    },
    {
        key: "priorite",
        label: "Priorité",
        type: "select",
        options: [
            { value: "BASSE", label: "Basse" },
            { value: "NORMALE", label: "Normale" },
            { value: "HAUTE", label: "Haute" },
            { value: "CRITIQUE", label: "Critique" },
        ],
    },
];

const {
    currentPage,
    pageSize,
    sortKey,
    sortOrder,
    filters: filtresActifs,
    filteredItems,
    paginatedItems,
    setPage,
    setPageSize,
    setSort,
    setFilters,
    resetFilters,
} = useTableData(tickets, {
    defaultPageSize: 25,
    defaultSortKey: "date_signalement",
    defaultSortOrder: "desc",
});

/*
 * Libellés lisibles.
 *
 * Ces tables reprennent les choix déclarés par le modèle Django. Une
 * valeur inconnue reste affichée telle quelle plutôt que masquée.
 */
const LIBELLES_TYPE = {
    MAINTENANCE: "Maintenance",
    RECLAMATION: "Réclamation",
};

const LIBELLES_STATUT = {
    OUVERT: "Ouvert",
    EN_COURS: "En cours",
    RESOLU: "Résolu",
    ANNULE: "Annulé",
};

const LIBELLES_PRIORITE = {
    BASSE: "Basse",
    NORMALE: "Normale",
    HAUTE: "Haute",
    CRITIQUE: "Critique",
};

function libelleType(valeur) {
    return LIBELLES_TYPE[valeur] || valeur || "—";
}

function libelleStatut(valeur) {
    return LIBELLES_STATUT[valeur] || valeur || "—";
}

function libellePriorite(valeur) {
    return LIBELLES_PRIORITE[valeur] || valeur || "—";
}

async function chargerTickets() {
    chargement.value = true;
    erreur.value = "";

    try {
        tickets.value = await getTickets();
    } catch (error) {
        console.error(
            "Erreur lors du chargement des tickets :",
            error
        );

        erreur.value =
            error.response?.data?.detail ||
            "Impossible de charger les tickets.";
    } finally {
        chargement.value = false;
    }
}

function ouvrirCreation() {
    afficherFormulaire.value = true;

    equipementSelectionne.value = "";
    titre.value = "";
    type.value = "MAINTENANCE";
    priorite.value = "NORMALE";
    description.value = "";
    erreurCreation.value = "";

    chargerEquipements();
}

async function chargerEquipements() {
    chargementEquipements.value = true;

    try {
        const tousLesEquipements =
            await getEquipementsDashboard();

        equipements.value = tousLesEquipements.filter(
            /*
             * Un équipement déjà en panne est refusé par l'API
             * ("Cet équipement est déjà en panne.") : il n'est donc pas
             * proposé, pour ne pas offrir une action qui échouerait.
             */
            (equipement) =>
                equipement.situation === "AFFECTE" &&
                equipement.etat !== "EN_PANNE"
        );
    } catch (error) {
        console.error(
            "Erreur lors du chargement des équipements :",
            error
        );

        erreurCreation.value =
            "Impossible de charger les équipements.";
    } finally {
        chargementEquipements.value = false;
    }
}

async function enregistrerTicket() {
    erreurCreation.value = "";

    if (!equipementSelectionne.value) {
        erreurCreation.value =
            "Veuillez sélectionner un équipement.";

        return;
    }

    if (!titre.value.trim()) {
        erreurCreation.value =
            "Veuillez saisir un titre.";

        return;
    }

    if (!description.value.trim()) {
        erreurCreation.value =
            "Veuillez saisir une description.";

        return;
    }

    creationEnCours.value = true;

    try {
        await creerTicket(
            equipementSelectionne.value,
            titre.value.trim(),
            description.value.trim(),
            type.value,
            priorite.value
        );

        notificationStore.success("Signalement créé avec succès");
        fermerFormulaire();

        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la création du signalement :",
            error
        );

        erreurCreation.value =
            error.response?.data?.detail ||
            "Impossible de créer le signalement.";
        notificationStore.error(erreurCreation.value);
    } finally {
        creationEnCours.value = false;
    }
}

function fermerFormulaire() {
    afficherFormulaire.value = false;

    equipementSelectionne.value = "";
    titre.value = "";
    type.value = "MAINTENANCE";
    priorite.value = "NORMALE";
    description.value = "";
    erreurCreation.value = "";
}

function ouvrirResolution(ticket) {
    ticketEnResolution.value = ticket;
    commentaireResolution.value = "";
    materielRepare.value = true;
    afficherModalResolution.value = true;
    erreurResolution.value = "";
}

function fermerModalResolution() {
    afficherModalResolution.value = false;
    ticketEnResolution.value = null;
    commentaireResolution.value = "";
    materielRepare.value = true;
    erreurResolution.value = "";
}

function ouvrirQualification(ticket) {
    ticketEnQualification.value = ticket;
    typeQualification.value = ticket.type;
    prioriteQualification.value = ticket.priorite;
    afficherModalQualification.value = true;
    erreurQualification.value = "";
}

function fermerModalQualification() {
    afficherModalQualification.value = false;
    ticketEnQualification.value = null;
    erreurQualification.value = "";
}

async function confirmerQualification() {
    qualificationEnCours.value = ticketEnQualification.value.id;
    erreurQualification.value = "";

    try {
        await qualifierTicket(ticketEnQualification.value.id, {
            type: typeQualification.value,
            priorite: prioriteQualification.value,
        });

        notificationStore.success("Signalement qualifié avec succès");
        fermerModalQualification();
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la qualification :",
            error
        );

        erreurQualification.value =
            error.response?.data?.detail ||
            "Impossible de qualifier le signalement.";
        notificationStore.error(erreurQualification.value);
    } finally {
        qualificationEnCours.value = null;
    }
}

async function confirmerResolution() {
    if (!commentaireResolution.value.trim()) {
        erreurResolution.value =
            "Veuillez saisir un commentaire de résolution.";
        return;
    }

    resolutionEnCours.value = ticketEnResolution.value.id;
    erreurResolution.value = "";

    try {
        await resoudreTicket(
            ticketEnResolution.value.id,
            commentaireResolution.value.trim(),
            materielRepare.value ? "EN_SERVICE" : "HORS_SERVICE"
        );

        notificationStore.success("Signalement résolu avec succès");
        fermerModalResolution();
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la résolution :",
            error
        );

        erreurResolution.value =
            error.response?.data?.detail ||
            "Impossible de résoudre le signalement.";
        notificationStore.error(erreurResolution.value);
    } finally {
        resolutionEnCours.value = null;
    }
}

/*
 * `date_resolution` n'est renseignée que pour un signalement résolu :
 * l'absence de date ne doit pas laisser croire à une donnée manquante.
 */
function formaterDate(date) {
    if (!date) {
        return "—";
    }

    return new Date(date).toLocaleString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

async function prendreEnCharge(ticket) {
    priseEnChargeEnCours.value = ticket.id;
    erreurAction.value = "";
    ticketEnErreur.value = null;

    try {
        await prendreEnChargeTicket(ticket.id);
        notificationStore.success("Signalement pris en charge");
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la prise en charge :",
            error
        );

        erreurAction.value =
            error.response?.data?.detail ||
            "Impossible de prendre en charge le signalement.";
        ticketEnErreur.value = ticket.id;
        notificationStore.error(erreurAction.value);
    } finally {
        priseEnChargeEnCours.value = null;
    }
}

onMounted(() => {
    chargerTickets();

    document.addEventListener("keydown", surTouche);
});

onBeforeUnmount(() => {
    document.removeEventListener("keydown", surTouche);
});

/*
 * Échap ferme la boîte de dialogue ouverte, comme le fait
 * `ConfirmDialog` ailleurs dans l'application.
 *
 * La fermeture est ignorée tant qu'une requête est en cours : la
 * boîte doit rester visible pour afficher son erreur.
 */
function surTouche(event) {
    if (event.key !== "Escape") {
        return;
    }

    if (afficherModalQualification.value && !qualificationEnCours.value) {
        fermerModalQualification();

        return;
    }

    if (afficherModalResolution.value && !resolutionEnCours.value) {
        fermerModalResolution();
    }
}
</script>

<style scoped>
.tickets-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.cellule-id {
    color: var(--text-light);
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}

.cellule-date {
    font-size: 0.8125rem;
    color: var(--text-muted);
    white-space: nowrap;
}

.ticket-titre {
    display: block;
    font-weight: 600;
    color: var(--text-main);
}

.ticket-equipement {
    display: block;
    margin-top: 0.1rem;
    color: var(--text-light);
    font-size: 0.75rem;
}

.actions-cellule {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

.champ-aide {
    margin: 0.35rem 0 0;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.modal__contexte {
    margin: 0 0 1rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.choix {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.4rem;
    color: var(--text-main);
    font-size: 0.875rem;
    cursor: pointer;
}

.choix input {
    margin-top: 0.2rem;
    flex-shrink: 0;
}

/* Les modales reprennent la boîte du design system. */
.modal-overlay {
    z-index: 1000;
    padding: 1.5rem;
}

.modal {
    width: 100%;
    max-width: 560px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 1.5rem;
}

.formulaire__groupe {
    margin: 0 0 1rem;
    padding: 0 0 0.25rem;
    border: none;
    border-bottom: 1px solid var(--border-light);
}

.formulaire__groupe:last-of-type {
    margin-bottom: 0;
    border-bottom: none;
}

@media (max-width: 640px) {
    .statistiques {
        grid-template-columns: 1fr 1fr;
    }

    .actions-cellule {
        flex-direction: column;
        align-items: stretch;
    }
}
</style>
