<template>
    <div class="plan-public-page">
        <div class="page-header">
            <div>
                <h1>Plan du système</h1>
                <p>Visualisation graphique des équipements</p>
            </div>
            <div class="header-actions">
                <router-link to="/dashboard-public" class="action-link">
                    ← Dashboard
                </router-link>
                <router-link to="/signaler" class="action-link">
                    → Signaler un problème
                </router-link>
                <router-link to="/login" class="action-link secondary">
                    → Connexion Admin
                </router-link>
            </div>
        </div>

        <!-- Navigation bâtiment/étage/salle -->
        <div class="navigation-bar">
            <div class="nav-section">
                <label for="batiment-select">Bâtiment :</label>
                <select
                    id="batiment-select"
                    v-model="batimentSelectionne"
                    @change="changerBatiment"
                >
                    <option value="">-- Sélectionner un bâtiment --</option>
                    <option
                        v-for="batiment in batiments"
                        :key="batiment.id"
                        :value="batiment.id"
                    >
                        {{ batiment.nom }}
                    </option>
                </select>
            </div>

            <div class="nav-section">
                <label for="etage-select">Étage :</label>
                <select
                    id="etage-select"
                    v-model="etageSelectionne"
                    @change="changerEtage"
                    :disabled="!batimentSelectionne"
                >
                    <option value="">-- Sélectionner un étage --</option>
                    <option
                        v-for="etage in etagesFiltres"
                        :key="etage.id"
                        :value="etage.id"
                    >
                        {{ etage.nom }}
                    </option>
                </select>
            </div>

            <div class="nav-section">
                <label for="salle-select">Salle :</label>
                <select
                    id="salle-select"
                    v-model="salleSelectionnee"
                    @change="changerSalle"
                    :disabled="!etageSelectionne"
                >
                    <option value="">-- Toutes les salles --</option>
                    <option
                        v-for="salle in sallesFiltrees"
                        :key="salle.id"
                        :value="salle.id"
                    >
                        {{ salle.nom }}
                    </option>
                </select>
            </div>

            <div class="nav-section">
                <label for="plan-select">Plan :</label>
                <select
                    id="plan-select"
                    v-model="planSelectionne"
                    :disabled="!etageSelectionne"
                >
                    <option value="">-- Sélectionner un plan --</option>
                    <option
                        v-for="plan in plansFiltres"
                        :key="plan.id"
                        :value="plan.id"
                    >
                        Plan {{ plan.nom }}
                    </option>
                </select>
            </div>
        </div>

        <!-- PlanViewer avec le plan sélectionné -->
        <div v-if="planSelectionne" class="plan-container">
            <PlanViewer
                :plan="planSelectionneObjet"
                :batiments="batiments"
                :etages="etages"
                :salles="salles"
                :equipements="equipements"
                :positions="positions"
                :est-admin="false"
                :equipement-a-mettre-en-evidence="equipementAMettreEnEvidence"
                @equipement-clic="voirEquipement"
            />
        </div>

        <div v-else class="no-plan-message">
            <p>Sélectionnez un bâtiment, un étage et un plan pour visualiser le plan graphique.</p>
        </div>

        <!-- Modal de détail d'équipement -->
        <div
            v-if="equipementSelectionne"
            class="modal-overlay"
            @click.self="fermerModal"
        >
            <div class="modal">
                <h2>{{ equipementSelectionne.nom }}</h2>

                <div class="info">
                    <strong>Type :</strong>
                    <span>{{ equipementSelectionne.type }}</span>
                </div>

                <div class="info">
                    <strong>N° inventaire :</strong>
                    <span>{{ equipementSelectionne.numero_inventaire }}</span>
                </div>

                <div class="info">
                    <strong>Fabricant :</strong>
                    <span>{{ equipementSelectionne.fabricant || '-' }}</span>
                </div>

                <div class="info">
                    <strong>Modèle :</strong>
                    <span>{{ equipementSelectionne.modele || '-' }}</span>
                </div>

                <div class="info">
                    <strong>État :</strong>
                    <span :class="`etat-${equipementSelectionne.etat.toLowerCase()}`">
                        {{ equipementSelectionne.etat }}
                    </span>
                </div>

                <div class="info">
                    <strong>Situation :</strong>
                    <span :class="`situation-${equipementSelectionne.situation.toLowerCase()}`">
                        {{ equipementSelectionne.situation }}
                    </span>
                </div>

                <div class="modal-actions">
                    <button
                        type="button"
                        @click="fermerModal"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>

        <NotificationToast />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getBatiments } from '../services/batimentService';
import { getEtages } from '../services/etageService';
import { getSalles } from '../services/salleService';
import { getPlans } from '../services/localisationService';
import { getEquipementsDashboard } from '../services/dashboardService';
import { getPositions } from '../services/localisationService';
import PlanViewer from '../components/PlanViewer.vue';
import NotificationToast from '../components/NotificationToast.vue';

const route = useRoute();
const batiments = ref([]);
const etages = ref([]);
const salles = ref([]);
const plans = ref([]);
const equipements = ref([]);
const positions = ref([]);
const equipementSelectionne = ref(null);
const equipementAMettreEnEvidence = ref(null);

const batimentSelectionne = ref("");
const etageSelectionne = ref("");
const salleSelectionnee = ref("");
const planSelectionne = ref("");

// Computed pour filtrer les étages selon le bâtiment
const etagesFiltres = computed(() => {
    if (!batimentSelectionne.value) return [];
    return etages.value.filter(etage => String(etage.batiment) === String(batimentSelectionne.value));
});

// Computed pour filtrer les salles selon l'étage
const sallesFiltrees = computed(() => {
    if (!etageSelectionne.value) return [];
    return salles.value.filter(salle => String(salle.etage) === String(etageSelectionne.value));
});

// Computed pour filtrer les plans selon l'étage
const plansFiltres = computed(() => {
    if (!etageSelectionne.value) return [];
    return plans.value.filter(plan => String(plan.etage) === String(etageSelectionne.value));
});

// Computed pour obtenir l'objet plan complet
const planSelectionneObjet = computed(() => {
    if (!planSelectionne.value) return null;
    return plans.value.find(plan => plan.id === planSelectionne.value) || null;
});

async function chargerDonnees() {
    try {
        batiments.value = await getBatiments();
        etages.value = await getEtages();
        salles.value = await getSalles();
        plans.value = await getPlans();
        equipements.value = await getEquipementsDashboard();
        positions.value = await getPositions();

        // Si un équipement est passé dans l'URL, naviguer automatiquement vers sa position
        const equipementId = route.query.equipementId;
        if (equipementId) {
            // Attendre un peu que les données soient chargées
            setTimeout(() => {
                naviguerVersEquipement(equipementId);
            }, 100);
        }
    } catch (error) {
        console.error('Erreur lors du chargement des données:', error);
    }
}

function naviguerVersEquipement(equipementId) {
    // Trouver la position de l'équipement
    const position = positions.value.find(p => String(p.equipement) === String(equipementId));
    if (!position) {
        console.log('Équipement non positionné');
        return;
    }

    // Trouver le plan de l'équipement
    const plan = plans.value.find(p => p.id === position.plan);
    if (!plan) {
        console.log('Plan non trouvé');
        return;
    }

    // Sélectionner l'étage du plan
    etageSelectionne.value = plan.etage;

    // Sélectionner le bâtiment de l'étage
    const etage = etages.value.find(e => e.id === plan.etage);
    if (etage) {
        batimentSelectionne.value = etage.batiment;
    }

    // Sélectionner le plan
    planSelectionne.value = plan.id;

    // Mettre l'équipement en évidence
    equipementAMettreEnEvidence.value = equipementId;
}

function changerBatiment() {
    etageSelectionne.value = "";
    salleSelectionnee.value = "";
    planSelectionne.value = "";
}

function changerEtage() {
    salleSelectionnee.value = "";
    planSelectionne.value = "";
}

function changerSalle() {
    // Si une salle est sélectionnée, filtrer par salle (optionnel)
}

function voirEquipement(equipement) {
    equipementSelectionne.value = equipement;
}

function fermerModal() {
    equipementSelectionne.value = null;
}

onMounted(() => {
    chargerDonnees();
});
</script>

<style scoped>
.plan-public-page {
    padding: 30px;
    min-height: 100vh;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
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

.header-actions {
    display: flex;
    gap: 10px;
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

.action-link.secondary {
    border-color: #6c757d;
    color: #6c757d;
}

.action-link.secondary:hover {
    background: #6c757d;
    color: white;
}

/* Navigation bar */
.navigation-bar {
    display: flex;
    gap: 20px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}

.nav-section {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.nav-section label {
    font-weight: 600;
    font-size: 14px;
    color: #333;
}

.nav-section select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 6px;
    background: white;
    min-width: 200px;
}

.nav-section select:disabled {
    background: #f5f5f5;
    color: #999;
}

.plan-container {
    margin-top: 20px;
}

.no-plan-message {
    text-align: center;
    padding: 60px 20px;
    background: #f8f9fa;
    border-radius: 8px;
    color: #666;
}

.no-plan-message p {
    font-size: 16px;
    margin: 0;
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
    margin-bottom: 20px;
}

.info {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #eee;
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
    background: #6c757d;
    color: white;
}

/* Badges d'état */
.etat-en_service {
    padding: 3px 8px;
    border-radius: 12px;
    background: #d4edda;
    color: #155724;
    font-size: 12px;
    font-weight: 600;
}

.etat-en_panne {
    padding: 3px 8px;
    border-radius: 12px;
    background: #f8d7da;
    color: #721c24;
    font-size: 12px;
    font-weight: 600;
}

.etat-en_maintenance {
    padding: 3px 8px;
    border-radius: 12px;
    background: #fff3cd;
    color: #856404;
    font-size: 12px;
    font-weight: 600;
}

.etat-hors_service {
    padding: 3px 8px;
    border-radius: 12px;
    background: #d6d8d9;
    color: #1b1e21;
    font-size: 12px;
    font-weight: 600;
}

/* Badges de situation */
.situation-affecte {
    padding: 3px 8px;
    border-radius: 12px;
    background: #cce5ff;
    color: #004085;
    font-size: 12px;
    font-weight: 600;
}

.situation-en_stock {
    padding: 3px 8px;
    border-radius: 12px;
    background: #e2e3e5;
    color: #383d41;
    font-size: 12px;
    font-weight: 600;
}
</style>
