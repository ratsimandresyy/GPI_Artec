<template>
    <div class="tickets-page">
        <div class="page-header">
            <div>
                <h1>Tickets</h1>
                <p>
                    Gestion des pannes et réclamations
                </p>
            </div>

            <button
                @click="ouvrirCreation"
            >
                Nouveau ticket
            </button>
        </div>

        <div
            v-if="afficherFormulaire"
            class="ticket-form"
        >
            <h2>Nouveau ticket</h2>

            <div class="form-group">
                <label for="equipement">
                Équipement
                </label>

                <select
                id="equipement"
                v-model="equipementSelectionne"
                :disabled="
                    chargementEquipements ||
                    creationEnCours
                "
                >
                <option value="">
                    -- Sélectionner un équipement --
                </option>

                <option
                    v-for="equipement in equipements"
                    :key="equipement.id"
                    :value="equipement.id"
                >
                    {{ equipement.nom }}
                    -
                    {{ equipement.numero_inventaire }}
                </option>
                </select>
            </div>

            <div class="form-group">
                <label for="titre">
                    Titre
                </label>

                <input
                    id="titre"
                    v-model="titre"
                    type="text"
                    placeholder="Titre du ticket..."
                    :disabled="creationEnCours"
                >
            </div>

            <div class="form-group">
                <label for="type">
                    Type
                </label>

                <select
                    id="type"
                    v-model="type"
                    :disabled="creationEnCours"
                >
                    <option value="MAINTENANCE">Maintenance</option>
                    <option value="RECLAMATION">Réclamation</option>
                </select>
            </div>

            <div class="form-group">
                <label for="priorite">
                    Priorité
                </label>

                <select
                    id="priorite"
                    v-model="priorite"
                    :disabled="creationEnCours"
                >
                    <option value="BASSE">Basse</option>
                    <option value="NORMALE">Normale</option>
                    <option value="HAUTE">Haute</option>
                    <option value="CRITIQUE">Critique</option>
                </select>
            </div>

            <div class="form-group">
                <label for="description">
                    Description
                </label>

                <textarea
                    id="description"
                    v-model="description"
                    rows="5"
                    placeholder="Décrivez la panne ou la réclamation..."
                    :disabled="creationEnCours"
        >       </textarea>
            </div>

            <p
                v-if="erreurCreation"
                class="message-error"
            >
                {{ erreurCreation }}
            </p>

            <div class="form-actions">
                <button
                    type="button"
                    @click="fermerFormulaire"
                    :disabled="creationEnCours"
            >
                Annuler
                </button>

                <button
                type="button"
                @click="enregistrerTicket"
                :disabled="creationEnCours"
            >
                {{
                    creationEnCours
                        ? "Création..."
                        : "Créer le ticket"
                }}
                </button>
            </div>
        </div>

        <div v-if="chargement" class="message">
            Chargement des tickets...
        </div>

        <div
            v-else-if="erreur"
            class="message message-error"
        >
            {{ erreur }}
        </div>

        <div
            v-else-if="tickets.length === 0"
            class="message"
        >
            Aucun ticket enregistré.
        </div>

        <div v-else class="tickets-list">
            <div
                v-for="ticket in tickets"
                :key="ticket.id"
                class="ticket-card"
            >
                <div class="ticket-header">
                    <strong>
                        #{{ ticket.id }} - {{ ticket.titre }}
                    </strong>

                    <div class="ticket-meta">
                        <span
                            class="statut"
                            :class="`statut-${ticket.statut.toLowerCase()}`"
                        >
                            {{ ticket.statut }}
                        </span>

                        <span
                            class="type"
                            :class="`type-${ticket.type.toLowerCase()}`"
                        >
                            {{ ticket.type }}
                        </span>

                        <span
                            class="priorite"
                            :class="`priorite-${ticket.priorite.toLowerCase()}`"
                        >
                            {{ ticket.priorite }}
                        </span>
                    </div>
                </div>

                <div class="ticket-content">
                    <p>
                        <strong>Équipement :</strong>
                        {{ ticket.equipement_nom }}
                    </p>

                    <p>
                        <strong>N° inventaire :</strong>
                        {{ ticket.numero_inventaire }}
                    </p>

                    <p>
                        <strong>Date :</strong>
                        {{ formaterDate(ticket.date_signalement) }}
                    </p>

                    <p>
                        <strong>Description :</strong>
                        {{ ticket.description }}
                    </p>
                </div>

                <div
                    v-if="estAdmin"
                    class="ticket-actions"
                >
                    <button
                        v-if="ticket.statut === 'OUVERT'"
                        type="button"
                        @click="prendreEnCharge(ticket)"
                        :disabled="
                            priseEnChargeEnCours === ticket.id
                        "
                    >
                        {{
                            priseEnChargeEnCours === ticket.id
                                ? "Prise en charge..."
                                : "Prendre en charge"
                        }}
                    </button>

                    <button
                        v-if="ticket.statut === 'EN_COURS'"
                        type="button"
                        @click="ouvrirResolution(ticket)"
                        :disabled="
                            resolutionEnCours === ticket.id
                        "
                    >
                        {{
                            resolutionEnCours === ticket.id
                                ? "Résolution..."
                                : "Résoudre"
                        }}
                    </button>

                    <button
                        v-if="ticket.statut !== 'RESOLU'"
                        type="button"
                        @click="ouvrirQualification(ticket)"
                        :disabled="
                            qualificationEnCours === ticket.id
                        "
                    >
                        {{
                            qualificationEnCours === ticket.id
                                ? "Qualification..."
                                : "Qualifier"
                        }}
                    </button>

                    <p
                        v-if="erreurAction"
                        class="message-error"
                    >
                        {{ erreurAction }}
                    </p>
                </div>
            </div>
        </div>

        <!-- Modal de résolution -->
        <div
            v-if="afficherModalResolution"
            class="modal-overlay"
            @click.self="fermerModalResolution"
        >
            <div class="modal">
                <h2>Résoudre le ticket</h2>

                <p v-if="ticketEnResolution">
                    <strong>{{ ticketEnResolution.titre }}</strong>
                </p>

                <div class="form-group">
                    <label for="commentaire">
                        Commentaire de résolution
                    </label>

                    <textarea
                        id="commentaire"
                        v-model="commentaireResolution"
                        rows="5"
                        placeholder="Décrivez la résolution..."
                        :disabled="resolutionEnCours"
                    ></textarea>
                </div>

                <!-- Diagramme d'activite : « Materiel repare ? »
                     Oui -> remise en service, Non -> reste hors service. -->
                <div class="form-group">
                    <span class="legend">
                        Matériel réparé ?
                    </span>

                    <label class="choice">
                        <input
                            v-model="materielRepare"
                            type="radio"
                            :value="true"
                            :disabled="resolutionEnCours"
                        >
                        Oui, remettre le matériel en service
                    </label>

                    <label class="choice">
                        <input
                            v-model="materielRepare"
                            type="radio"
                            :value="false"
                            :disabled="resolutionEnCours"
                        >
                        Non, maintenir le matériel hors service
                    </label>
                </div>

                <p
                    v-if="erreurAction"
                    class="message-error"
                >
                    {{ erreurAction }}
                </p>

                <div class="modal-actions">
                    <button
                        type="button"
                        @click="fermerModalResolution"
                        :disabled="resolutionEnCours"
                    >
                        Annuler
                    </button>

                    <button
                        type="button"
                        @click="confirmerResolution"
                        :disabled="resolutionEnCours"
                    >
                        {{
                            resolutionEnCours
                                ? "Résolution..."
                                : "Résoudre"
                        }}
                    </button>
                </div>
            </div>
        </div>

        <!-- Modal de qualification : diagramme d'activite
             « Qualifier le ticket : definir le type, definir la priorite ». -->
        <div
            v-if="afficherModalQualification"
            class="modal-overlay"
            @click.self="fermerModalQualification"
        >
            <div class="modal">
                <h2>Qualifier le ticket</h2>

                <p v-if="ticketEnQualification">
                    <strong>{{ ticketEnQualification.titre }}</strong>
                </p>

                <div class="form-group">
                    <label for="qualification-type">
                        Type
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

                <p
                    v-if="erreurAction"
                    class="message-error"
                >
                    {{ erreurAction }}
                </p>

                <div class="modal-actions">
                    <button
                        type="button"
                        @click="fermerModalQualification"
                        :disabled="qualificationEnCours"
                    >
                        Annuler
                    </button>

                    <button
                        type="button"
                        @click="confirmerQualification"
                        :disabled="qualificationEnCours"
                    >
                        {{
                            qualificationEnCours
                                ? "Qualification..."
                                : "Qualifier"
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
    getTickets,
    creerTicket,
    prendreEnChargeTicket,
    resoudreTicket,
    qualifierTicket,
} from "../services/ticketService";

import {
    getEquipementsDashboard,
} from "../services/dashboardService";

import { useAuthStore } from "../stores/auth";
import { useNotificationStore } from "../stores/notifications";

const tickets = ref([]);
const chargement = ref(false);
const erreur = ref("");

const authStore = useAuthStore();
const notificationStore = useNotificationStore();

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
const erreurAction = ref("");

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
const qualificationEnCours = ref(null);

const estAdmin = computed(
    () => authStore.user?.role === "ADMIN"
);

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
            (equipement) =>
                equipement.situation === "AFFECTE"
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

        notificationStore.success("Ticket créé avec succès");
        fermerFormulaire();

        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la création du ticket :",
            error
        );

        erreurCreation.value =
            error.response?.data?.detail ||
            "Impossible de créer le ticket.";
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
    erreurAction.value = "";
}

function fermerModalResolution() {
    afficherModalResolution.value = false;
    ticketEnResolution.value = null;
    commentaireResolution.value = "";
    materielRepare.value = true;
    erreurAction.value = "";
}

function ouvrirQualification(ticket) {
    ticketEnQualification.value = ticket;
    typeQualification.value = ticket.type;
    prioriteQualification.value = ticket.priorite;
    afficherModalQualification.value = true;
    erreurAction.value = "";
}

function fermerModalQualification() {
    afficherModalQualification.value = false;
    ticketEnQualification.value = null;
    erreurAction.value = "";
}

async function confirmerQualification() {
    qualificationEnCours.value = ticketEnQualification.value.id;
    erreurAction.value = "";

    try {
        await qualifierTicket(ticketEnQualification.value.id, {
            type: typeQualification.value,
            priorite: prioriteQualification.value,
        });

        notificationStore.success("Ticket qualifié avec succès");
        fermerModalQualification();
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la qualification :",
            error
        );

        erreurAction.value =
            error.response?.data?.detail ||
            "Impossible de qualifier le ticket.";
        notificationStore.error(erreurAction.value);
    } finally {
        qualificationEnCours.value = null;
    }
}

async function confirmerResolution() {
    if (!commentaireResolution.value.trim()) {
        erreurAction.value = "Veuillez saisir un commentaire de résolution.";
        return;
    }

    resolutionEnCours.value = ticketEnResolution.value.id;
    erreurAction.value = "";

    try {
        await resoudreTicket(
            ticketEnResolution.value.id,
            commentaireResolution.value.trim(),
            materielRepare.value ? "EN_SERVICE" : "HORS_SERVICE"
        );

        notificationStore.success("Ticket résolu avec succès");
        fermerModalResolution();
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la résolution :",
            error
        );

        erreurAction.value =
            error.response?.data?.detail ||
            "Impossible de résoudre le ticket.";
        notificationStore.error(erreurAction.value);
    } finally {
        resolutionEnCours.value = null;
    }
}

function formaterDate(date) {
    if (!date) return "-";
    return new Date(date).toLocaleString("fr-FR");
}

async function prendreEnCharge(ticket) {
    priseEnChargeEnCours.value = ticket.id;
    erreurAction.value = "";

    try {
        await prendreEnChargeTicket(ticket.id);
        notificationStore.success("Ticket pris en charge avec succès");
        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la prise en charge :",
            error
        );

        erreurAction.value =
            error.response?.data?.detail ||
            "Impossible de prendre en charge le ticket.";
        notificationStore.error(erreurAction.value);
    } finally {
        priseEnChargeEnCours.value = null;
    }
}

onMounted(() => {
    chargerTickets();
});
</script>

<style scoped>
.tickets-page {
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.page-header h1 {
    margin: 0;
}

.page-header p {
    margin: 5px 0 0;
    color: #666;
}

.page-header button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background: #2563eb;
    color: white;
    cursor: pointer;
}

.tickets-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.ticket-card {
    padding: 18px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.ticket-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.ticket-meta {
    display: flex;
    gap: 8px;
    align-items: center;
}

.ticket-content p {
    margin: 7px 0;
}

.statut {
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
}

.type {
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
    background: #e9ecef;
}

.type-maintenance {
    background: #d1ecf1;
    color: #0c5460;
}

.type-reclamation {
    background: #f8d7da;
    color: #721c24;
}

.priorite {
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
}

.priorite-basse {
    background: #d4edda;
    color: #155724;
}

.priorite-normale {
    background: #fff3cd;
    color: #856404;
}

.priorite-haute {
    background: #f5c6cb;
    color: #721c24;
}

.priorite-critique {
    background: #d6d8d9;
    color: #1b1e21;
}

.message {
    padding: 20px;
    text-align: center;
    color: #666;
}

.message-error {
    color: #b00020;
}

.ticket-actions {
    display: flex;
    align-items: center;
    gap: 15px;

    margin-top: 15px;
    padding-top: 15px;

    border-top: 1px solid #eee;
}

.ticket-actions button {
    padding: 8px 14px;

    border: none;
    border-radius: 6px;

    background: #2563eb;
    color: white;

    cursor: pointer;
}

.ticket-actions button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Modal styles */
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
    width: 500px;
    max-width: 90%;
    padding: 25px;
    background: white;
    border-radius: 10px;
}

.modal h2 {
    margin-top: 0;
    margin-bottom: 15px;
}

.form-group {
    margin-bottom: 15px;
}

.legend {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
}

.choice {
    display: block;
    margin-bottom: 5px;
    font-weight: normal;
    cursor: pointer;
}

.choice input {
    margin-right: 8px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
}

.modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.modal-actions button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.modal-actions button:last-child {
    background: #2563eb;
    color: white;
}

.modal-actions button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>