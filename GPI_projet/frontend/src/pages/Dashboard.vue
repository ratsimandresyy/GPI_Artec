<template>
    <div class="dashboard">

        <div class="dashboard-header">
            <div>
                <h1>Dashboard</h1>
                <p>Vue générale du parc informatique</p>
            </div>

            <button
                type="button"
                class="refresh-button"
                @click="chargerDashboard"
            >
                Actualiser
            </button>
        </div>

        <!-- Chargement -->
        <div v-if="loading" class="message">
            Chargement des données...
        </div>

        <!-- Erreur -->
        <div v-else-if="errorMessage" class="message error">
            {{ errorMessage }}
        </div>

        <!-- Contenu -->
        <div v-else>

            <div class="statistics-grid">

                <div class="stat-card">
                    <div class="stat-title">
                        Équipements
                    </div>

                    <div class="stat-value">
                        {{ statistiques.equipements }}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">
                        Équipements actifs
                    </div>

                    <div class="stat-value">
                        {{ statistiques.equipementsActifs }}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">
                        Bâtiments
                    </div>

                    <div class="stat-value">
                        {{ statistiques.batiments }}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">
                        Étages
                    </div>

                    <div class="stat-value">
                        {{ statistiques.etages }}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">
                        Salles
                    </div>

                    <div class="stat-value">
                        {{ statistiques.salles }}
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-title">
                        Rapports d'audit
                    </div>

                    <div class="stat-value">
                        {{ statistiques.audits }}
                    </div>
                </div>

            </div>

            <div class="dashboard-section">

                <h2>Équipements récents</h2>

                <div
                    v-if="equipementsRecents.length === 0"
                    class="empty-message"
                >
                    Aucun équipement enregistré.
                </div>

                <table v-else>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nom</th>
                            <th>Numéro d'inventaire</th>
                            <th>Fabricant</th>
                            <th>Modèle</th>
                            <th>État</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr
                            v-for="equipement in equipementsRecents"
                            :key="equipement.id"
                        >
                            <td>{{ equipement.id }}</td>

                            <td>{{ equipement.nom }}</td>

                            <td>
                                {{ equipement.numero_inventaire }}
                            </td>

                            <td>
                                {{ equipement.fabricant || "-" }}
                            </td>

                            <td>
                                {{ equipement.modele || "-" }}
                            </td>

                            <td>
                                <span
                                    :class="[
                                        'status',
                                        equipement.actif
                                            ? 'active'
                                            : 'inactive'
                                    ]"
                                >
                                    {{
                                        equipement.actif
                                            ? "Actif"
                                            : "Inactif"
                                    }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>

        </div>

    </div>
</template>


<script setup>

import { ref, onMounted } from "vue";

import {
    getEquipementsDashboard,
    getBatimentsDashboard,
    getEtagesDashboard,
    getSallesDashboard,
    getRapportsAuditDashboard,
} from "../services/dashboardService";


const loading = ref(false);

const errorMessage = ref("");

const equipements = ref([]);
const batiments = ref([]);
const etages = ref([]);
const salles = ref([]);
const audits = ref([]);


const statistiques = ref({
    equipements: 0,
    equipementsActifs: 0,
    batiments: 0,
    etages: 0,
    salles: 0,
    audits: 0,
});


const equipementsRecents = ref([]);


/**
 * Charge toutes les données nécessaires
 * au dashboard.
 */
async function chargerDashboard() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const [
            donneesEquipements,
            donneesBatiments,
            donneesEtages,
            donneesSalles,
            donneesAudits,
        ] = await Promise.all([
            getEquipementsDashboard(),
            getBatimentsDashboard(),
            getEtagesDashboard(),
            getSallesDashboard(),
            getRapportsAuditDashboard(),
        ]);


        equipements.value = donneesEquipements;
        batiments.value = donneesBatiments;
        etages.value = donneesEtages;
        salles.value = donneesSalles;
        audits.value = donneesAudits;


        statistiques.value = {

            equipements: equipements.value.length,

            equipementsActifs:
                equipements.value.filter(
                    (equipement) => equipement.actif
                ).length,

            batiments: batiments.value.length,

            etages: etages.value.length,

            salles: salles.value.length,

            audits: audits.value.length,
        };


        /*
         * On affiche au maximum les 5 derniers équipements.
         *
         * Pour l'instant, on utilise l'ordre retourné
         * par l'API.
         */
        equipementsRecents.value =
            equipements.value.slice(-5).reverse();

    } catch (error) {

        console.error(
            "Erreur lors du chargement du dashboard :",
            error
        );

        errorMessage.value =
            "Impossible de charger les données du dashboard.";

    } finally {

        loading.value = false;
    }
}


onMounted(() => {
    chargerDashboard();
});

</script>


<style scoped>

.dashboard {
    width: 100%;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.dashboard-header h1 {
    margin: 0;
    font-size: 28px;
}

.dashboard-header p {
    margin-top: 6px;
    color: #666;
}

.refresh-button {
    padding: 10px 18px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: white;
    cursor: pointer;
}

.refresh-button:hover {
    background: #f5f5f5;
}

.statistics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-bottom: 35px;
}

.stat-card {
    padding: 22px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}

.stat-title {
    color: #666;
    font-size: 14px;
    margin-bottom: 10px;
}

.stat-value {
    font-size: 30px;
    font-weight: bold;
}

.dashboard-section {
    margin-top: 20px;
}

.dashboard-section h2 {
    margin-bottom: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: white;
}

th,
td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}

th {
    font-weight: bold;
}

.status {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 5px;
    font-size: 13px;
}

.status.active {
    background: #e8f5e9;
}

.status.inactive {
    background: #ffebee;
}

.message {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
}

.message.error {
    border-color: #d9534f;
}

.empty-message {
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    color: #666;
}

@media (max-width: 900px) {

    .statistics-grid {
        grid-template-columns: repeat(2, 1fr);
    }

}

@media (max-width: 600px) {

    .statistics-grid {
        grid-template-columns: 1fr;
    }

}

</style>