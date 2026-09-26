<template>
    <div class="ticket-public-page">
        <div class="page-header">
            <div>
                <h1>Signaler un problème</h1>
                <p>Formulaire de signalement pour les visiteurs</p>
            </div>
            <div class="header-actions">
                <router-link to="/dashboard-public" class="action-link">
                    ← Dashboard
                </router-link>
                <router-link to="/plan" class="action-link">
                    → Voir le plan du système
                </router-link>
            </div>
        </div>

        <div class="ticket-container">
            <div class="ticket-form">
                <h2>Créer un ticket de panne</h2>

                <form @submit.prevent="enregistrer">
                    <div class="form-group">
                        <label for="equipement">Équipement concerné *</label>
                        <select
                            id="equipement"
                            v-model="equipementSelectionne"
                            :disabled="chargementEquipements || creationEnCours"
                            required
                        >
                            <option value="">
                                -- Sélectionner un équipement --
                            </option>

                            <option
                                v-for="equipement in equipements"
                                :key="equipement.id"
                                :value="equipement.id"
                            >
                                {{ equipement.nom }} - {{ equipement.numero_inventaire }}
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="titre">Titre *</label>
                        <input
                            id="titre"
                            v-model="titre"
                            type="text"
                            placeholder="Titre du problème..."
                            :disabled="creationEnCours"
                            required
                        >
                    </div>

                    <div class="form-group">
                        <label for="type">Type</label>
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
                        <label for="priorite">Priorité</label>
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
                        <label for="description">Description du problème *</label>
                        <textarea
                            id="description"
                            v-model="description"
                            rows="5"
                            placeholder="Décrivez le problème rencontré..."
                            :disabled="creationEnCours"
                            required
                        ></textarea>
                    </div>

                    <p v-if="erreurCreation" class="error">
                        {{ erreurCreation }}
                    </p>

                    <p v-if="succesCreation" class="success">
                        ✅ Ticket créé avec succès ! L'équipe technique en a été notifiée.
                    </p>

                    <div class="form-actions">
                        <button
                            type="submit"
                            class="primary-button"
                            :disabled="creationEnCours"
                        >
                            {{ creationEnCours ? "Création..." : "Envoyer le signalement" }}
                        </button>
                    </div>
                </form>
            </div>

            <div class="info-card">
                <h3>Informations</h3>
                <p>
                    Ce formulaire permet de signaler un problème sur un équipement informatique sans se connecter.
                </p>
                <p>
                    Les administrateurs seront notifiés et pourront traiter votre demande.
                </p>
                <p>
                    Pour suivre l'avancement de votre ticket, veuillez contacter un administrateur.
                </p>
            </div>
        </div>

        <NotificationToast />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { creerTicket } from '../services/ticketService';
import { getEquipementsDashboard } from '../services/dashboardService';
import { useNotificationStore } from '../stores/notifications';
import NotificationToast from '../components/NotificationToast.vue';

const notificationStore = useNotificationStore();

const equipements = ref([]);
const equipementSelectionne = ref("");
const titre = ref("");
const type = ref("MAINTENANCE");
const priorite = ref("NORMALE");
const description = ref("");

const chargementEquipements = ref(false);
const creationEnCours = ref(false);
const erreurCreation = ref("");
const succesCreation = ref(false);

async function chargerEquipements() {
    chargementEquipements.value = true;

    try {
        const tousLesEquipements = await getEquipementsDashboard();
        equipements.value = tousLesEquipements.filter(
            (equipement) => equipement.situation === "AFFECTE"
        );
    } catch (error) {
        console.error(
            "Erreur lors du chargement des équipements :",
            error
        );
        erreurCreation.value = "Impossible de charger les équipements.";
    } finally {
        chargementEquipements.value = false;
    }
}

async function enregistrer() {
    erreurCreation.value = "";
    succesCreation.value = false;

    if (!equipementSelectionne.value) {
        erreurCreation.value = "Veuillez sélectionner un équipement.";
        return;
    }

    if (!titre.value.trim()) {
        erreurCreation.value = "Veuillez saisir un titre.";
        return;
    }

    if (!description.value.trim()) {
        erreurCreation.value = "Veuillez saisir une description.";
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

        notificationStore.success("Ticket créé avec succès ! L'équipe technique en a été notifiée.");
        succesCreation.value = true;

        // Réinitialiser le formulaire
        equipementSelectionne.value = "";
        titre.value = "";
        type.value = "MAINTENANCE";
        priorite.value = "NORMALE";
        description.value = "";
    } catch (error) {
        console.error(
            "Erreur lors de la création du ticket :",
            error
        );
        erreurCreation.value = error.response?.data?.detail || "Impossible de créer le ticket.";
        notificationStore.error(erreurCreation.value);
    } finally {
        creationEnCours.value = false;
    }
}

onMounted(() => {
    chargerEquipements();
});
</script>

<style scoped>
.ticket-public-page {
    padding: 30px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    margin-bottom: 30px;
}

.page-header h1 {
    margin: 0;
    font-size: 28px;
}

.page-header p {
    margin: 5px 0 0;
    color: #666;
}

.ticket-container {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
}

.ticket-form {
    padding: 30px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.ticket-form h2 {
    margin-top: 0;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 15px;
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

.form-actions {
    margin-top: 20px;
}

.primary-button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background: #222;
    color: white;
    cursor: pointer;
}

.primary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.info-card {
    padding: 30px;
    background: #f8f9fa;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.info-card h3 {
    margin-top: 0;
    margin-bottom: 15px;
}

.info-card p {
    margin-bottom: 10px;
    line-height: 1.6;
}

.error {
    color: #b00020;
    margin-top: 10px;
}

.success {
    color: #16803c;
    margin-top: 10px;
    font-weight: 600;
}

.action-link {
    padding: 10px 16px;
    border: 1px solid #222;
    border-radius: 6px;
    color: #222;
    text-decoration: none;
    font-weight: 600;
}

.action-link:hover {
    background: #222;
    color: white;
}

@media (max-width: 768px) {
    .ticket-container {
        grid-template-columns: 1fr;
    }
}
</style>
