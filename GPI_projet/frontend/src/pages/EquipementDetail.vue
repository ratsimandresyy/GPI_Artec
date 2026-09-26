<template>
    <div class="equipement-detail">

        <div class="back-button-container">
            <button @click="retour" class="back-button">
                ← Retour
            </button>
        </div>

        <div class="page-header">
            <div>
                <h1>Détail de l'équipement</h1>
                <p v-if="equipement">{{ equipement.nom }}</p>
            </div>

            <div v-if="estAdmin" class="header-actions">
                <button
                    type="button"
                    class="action-button danger"
                    @click="supprimer"
                >
                    Supprimer
                </button>
            </div>
        </div>

        <!-- Chargement -->
        <p v-if="loading">
            Chargement...
        </p>

        <!-- Erreur -->
        <p v-else-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>

        <!-- Informations -->
        <div v-else-if="equipement" class="card">

            <div class="section">
                <h3>Informations générales</h3>

                <div class="information">
                    <strong>ID :</strong>
                    <span>{{ equipement.id }}</span>
                </div>

                <div class="information">
                    <strong>Type :</strong>
                    <span>{{ equipement.type }}</span>
                </div>

                <div class="information">
                    <strong>Numéro d'inventaire :</strong>
                    <span>
                        {{ equipement.numero_inventaire }}
                    </span>
                </div>

                <div class="information">
                    <strong>Numéro de série :</strong>
                    <span>
                        {{ equipement.numero_serie || "-" }}
                    </span>
                </div>

                <div class="information">
                    <strong>Fabricant :</strong>
                    <span>
                        {{ equipement.fabricant || "-" }}
                    </span>
                </div>

                <div class="information">
                    <strong>Modèle :</strong>
                    <span>
                        {{ equipement.modele || "-" }}
                    </span>
                </div>
            </div>

            <div class="section">
                <h3>Réseau</h3>

                <div class="information">
                    <strong>Adresse IP :</strong>
                    <span>
                        {{ equipement.adresse_ip || "-" }}
                    </span>
                </div>

                <div class="information">
                    <strong>Adresse MAC :</strong>
                    <span>
                        {{ equipement.adresse_mac || "-" }}
                    </span>
                </div>
            </div>

            <div class="section">
                <h3>Localisation</h3>

                <div class="information">
                    <strong>Salle :</strong>
                    <span>
                        {{ equipement.salle || "-" }}
                    </span>
                </div>

                <div class="information">
                    <strong>État :</strong>
                    <span :class="`etat-${equipement.etat.toLowerCase()}`">
                        {{ equipement.etat || "-"}}
                    </span>
                </div>

                <div class="information">
                    <strong>Situation :</strong>
                    <span :class="`situation-${equipement.situation.toLowerCase()}`">
                        {{ equipement.situation || "-"}}
                    </span>
                </div>

                <div class="information" v-if="equipement.condition_stock">
                    <strong>Condition du stock :</strong>
                    <span>
                        {{ equipement.condition_stock }}
                    </span>
                </div>
            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import { getEquipement, supprimerEquipement } from "../services/equipementService";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const equipement = ref(null);
const loading = ref(false);
const errorMessage = ref("");

const estAdmin = computed(() => authStore.isAdmin);

/**
 * Récupère l'identifiant présent dans l'URL.
 */
const id = route.params.id;

/**
 * Charge l'équipement depuis l'API.
 */
async function chargerEquipement() {
    loading.value = true;
    errorMessage.value = "";

    try {
        equipement.value = await getEquipement(id);

    } catch (error) {

        console.error(
            "Erreur lors du chargement de l'équipement :",
            error
        );

        errorMessage.value =
            "Impossible de charger cet équipement.";

    } finally {
        loading.value = false;
    }
}

/**
 * Retourne à la liste des équipements ou au dashboard public.
 */
function retour() {
    if (estAdmin.value) {
        router.push("/equipements");
    } else {
        router.push("/dashboard-public");
    }
}

async function supprimer() {
    const confirmation = window.confirm(
        `Voulez-vous vraiment supprimer l'équipement "${equipement.value.nom}" ?`
    );

    if (!confirmation) {
        return;
    }

    try {
        await supprimerEquipement(id);
        router.push("/equipements");
    } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        errorMessage.value = error.response?.data?.detail || "Impossible de supprimer l'équipement.";
    }
}

onMounted(() => {
    chargerEquipement();
});
</script>

<style scoped>

.back-button-container {
    margin-bottom: 20px;
}

.back-button {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    background: #eee;
    color: #333;
    cursor: pointer;
    font-size: 14px;
}

.back-button:hover {
    background: #ddd;
}

.equipement-detail {
    padding: 30px;
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

.visitor-note {
    font-size: 12px;
    color: #666;
    font-style: italic;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.action-button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.action-button.danger {
    background: #dc3545;
    color: white;
}

.action-button:not(.danger) {
    background: #6c757d;
    color: white;
}

.card {
    max-width: 700px;
    margin-top: 20px;
    padding: 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.section {
    margin-bottom: 30px;
}

.section h3 {
    margin-top: 0;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #eee;
}

.information {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #eee;
}

.error {
    color: red;
}

button {
    padding: 8px 15px;
    cursor: pointer;
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