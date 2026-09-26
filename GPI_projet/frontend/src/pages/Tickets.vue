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
                v-if="estAdmin"
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
                        Ticket #{{ ticket.id }}
                    </strong>

                    <span
                        class="statut"
                        :class="`statut-${ticket.statut.toLowerCase()}`"
                    >
                        {{ ticket.statut }}
                    </span>
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
                        {{ ticket.date_signalement }}
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

                    <p
                        v-if="erreurAction"
                        class="message-error"
                    >
                        {{ erreurAction }}
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {
    ref,
    onMounted,
} from "vue";

import {
    getTickets, creerTicket, prendreEnChargeTicket
} from "../services/ticketService";

import {
    getEquipementsDashboard,
} from "../services/dashboardService";

import { useAuthStore } from "../stores/auth";

const tickets = ref([]);
const chargement = ref(false);
const erreur = ref("");

const afficherFormulaire = ref(false);

const equipements = ref([]);
const chargementEquipements = ref(false);

const equipementSelectionne = ref("");
const description = ref("");

const creationEnCours = ref(false);
const erreurCreation = ref("");

const priseEnChargeEnCours = ref(null);
const erreurAction = ref("");

const authStore = useAuthStore();

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

    if (!description.value.trim()) {
        erreurCreation.value =
            "Veuillez saisir une description.";

        return;
    }

    creationEnCours.value = true;

    try {
        await creerTicket(
            equipementSelectionne.value,
            description.value.trim()
        );

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
    } finally {
        creationEnCours.value = false;
    }
}

function fermerFormulaire() {
    afficherFormulaire.value = false;

    equipementSelectionne.value = "";
    description.value = "";
    erreurCreation.value = "";
}

async function prendreEnCharge(ticket) {
    priseEnChargeEnCours.value = ticket.id;
    erreurAction.value = "";

    try {
        await prendreEnChargeTicket(ticket.id);

        await chargerTickets();
    } catch (error) {
        console.error(
            "Erreur lors de la prise en charge :",
            error
        );

        erreurAction.value =
            error.response?.data?.detail ||
            "Impossible de prendre en charge le ticket.";
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

.ticket-content p {
    margin: 7px 0;
}

.statut {
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: bold;
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
</style>