<script setup>
import { ref, onMounted } from "vue";

import {
    getEquipementsDashboard,
    getBatimentsDashboard,
    getEtagesDashboard,
    getSallesDashboard,
    getRapportsAuditDashboard,
} from "../services/dashboardService";

// Statistiques
const nombreEquipements = ref(0);
const nombreBatiments = ref(0);
const nombreEtages = ref(0);
const nombreSalles = ref(0);
const nombreAudits = ref(0);

// État de la page
const chargement = ref(true);
const erreur = ref("");

/**
 * Charge les données nécessaires au Dashboard.
 */
async function chargerDashboard() {
    chargement.value = true;
    erreur.value = "";

    try {
        const [
            equipements,
            batiments,
            etages,
            salles,
            audits,
        ] = await Promise.all([
            getEquipementsDashboard(),
            getBatimentsDashboard(),
            getEtagesDashboard(),
            getSallesDashboard(),
            getRapportsAuditDashboard(),
        ]);

        nombreEquipements.value = equipements.length;
        nombreBatiments.value = batiments.length;
        nombreEtages.value = etages.length;
        nombreSalles.value = salles.length;
        nombreAudits.value = audits.length;

    } catch (error) {
        console.error(
            "Erreur lors du chargement du Dashboard :",
            error
        );

        erreur.value =
            "Impossible de charger les données du tableau de bord.";

    } finally {
        chargement.value = false;
    }
}

onMounted(() => {
    chargerDashboard();
});
</script>

<template>
    <div class="dashboard">

        <!-- En-tête -->
        <div class="dashboard-header">
            <h1>Tableau de bord</h1>

            <p>
                Vue d'ensemble du parc informatique
            </p>
        </div>

        <!-- Chargement -->
        <div
            v-if="chargement"
            class="message"
        >
            Chargement des données...
        </div>

        <!-- Erreur -->
        <div
            v-else-if="erreur"
            class="message erreur"
        >
            {{ erreur }}
        </div>

        <!-- Dashboard -->
        <template v-else>

            <!-- Statistiques -->
            <div class="statistiques">

                <div class="carte-statistique">
                    <div class="icone">💻</div>

                    <div>
                        <p>Équipements</p>
                        <h2>{{ nombreEquipements }}</h2>
                    </div>
                </div>

                <div class="carte-statistique">
                    <div class="icone">🏢</div>

                    <div>
                        <p>Bâtiments</p>
                        <h2>{{ nombreBatiments }}</h2>
                    </div>
                </div>

                <div class="carte-statistique">
                    <div class="icone">🏠</div>

                    <div>
                        <p>Étages</p>
                        <h2>{{ nombreEtages }}</h2>
                    </div>
                </div>

                <div class="carte-statistique">
                    <div class="icone">🚪</div>

                    <div>
                        <p>Salles</p>
                        <h2>{{ nombreSalles }}</h2>
                    </div>
                </div>

                <div class="carte-statistique">
                    <div class="icone">📋</div>

                    <div>
                        <p>Rapports d'audit</p>
                        <h2>{{ nombreAudits }}</h2>
                    </div>
                </div>

            </div>

            <!-- Résumé -->
            <div class="resume">

                <h2>Résumé du parc</h2>

                <p>
                    Le système contient actuellement
                    <strong>{{ nombreEquipements }}</strong>
                    équipement(s) informatique(s), réparti(s) dans
                    <strong>{{ nombreSalles }}</strong>
                    salle(s) et
                    <strong>{{ nombreBatiments }}</strong>
                    bâtiment(s).
                </p>

                <p>
                    Le système comprend également
                    <strong>{{ nombreEtages }}</strong>
                    étage(s) et
                    <strong>{{ nombreAudits }}</strong>
                    rapport(s) d'audit.
                </p>

            </div>

        </template>

    </div>
</template>

<style scoped>

.dashboard {
    padding: 30px;
}

.dashboard-header {
    margin-bottom: 30px;
}

.dashboard-header h1 {
    margin: 0;
    font-size: 32px;
}

.dashboard-header p {
    margin-top: 8px;
    color: var(--text-muted);
}

/* Statistiques */

.statistiques {
    display: grid;

    grid-template-columns:
        repeat(auto-fit, minmax(190px, 1fr));

    gap: 20px;

    margin-bottom: 30px;
}

.carte-statistique {
    display: flex;
    align-items: center;

    gap: 18px;

    padding: 22px;

    background: var(--bg-surface);

    border-radius: 10px;

    box-shadow:
        var(--shadow-md);
}

.icone {
    font-size: 32px;
}

.carte-statistique p {
    margin: 0 0 5px;

    color: var(--text-muted);
}

.carte-statistique h2 {
    margin: 0;

    font-size: 28px;
}

/* Résumé */

.resume {
    padding: 25px;

    background: var(--bg-surface);

    border-radius: 10px;

    box-shadow:
        var(--shadow-md);
}

.resume h2 {
    margin-top: 0;
}

.resume p {
    line-height: 1.6;

    color: var(--text-main);
}

/* Messages */

.message {
    padding: 20px;

    background: var(--bg-surface);

    border-radius: 10px;
}

.erreur {
    color: var(--danger-text);
}

</style>