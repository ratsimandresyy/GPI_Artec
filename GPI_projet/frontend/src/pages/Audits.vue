<template>
    <div class="audits-page">

        <div class="page-header">
            <div>
                <h1>Audits WinAudit</h1>
                <p>
                    Historique des informations collectées sur les équipements.
                </p>
            </div>

            <div class="header-actions">
                <select
                    v-model="filtreEquipement"
                    @change="filtrerAudits"
                    class="filter-select"
                >
                    <option value="">Tous les équipements</option>
                    <option
                        v-for="equipement in equipementsUniques"
                        :key="equipement"
                        :value="equipement"
                    >
                        {{ equipement }}
                    </option>
                </select>

                <button
                    class="btn-refresh"
                    @click="chargerAudits"
                >
                    Actualiser
                </button>
            </div>
        </div>


        <div v-if="chargement" class="message">
            Chargement des audits...
        </div>


        <div v-else-if="erreur" class="message erreur">
            {{ erreur }}
        </div>


        <div
            v-else-if="auditsFiltres.length === 0"
            class="message"
        >
            Aucun rapport d'audit disponible.
        </div>


        <div v-else class="audit-layout">

            <!-- LISTE DES AUDITS -->

            <div class="audit-list">

                <div
                    v-for="audit in auditsFiltres"
                    :key="audit.id"
                    class="audit-card"
                    :class="{
                        selected:
                            auditSelectionne?.id === audit.id
                    }"
                    @click="selectionnerAudit(audit)"
                >

                    <div class="audit-card-header">

                        <strong>
                            {{ audit.equipement_nom || "Équipement inconnu" }}
                        </strong>

                        <span>
                            #{{ audit.id }}
                        </span>

                    </div>

                    <div class="audit-card-body">

                        <p>
                            <strong>Inventaire :</strong>
                            {{ audit.numero_inventaire || "-" }}
                        </p>

                        <p>
                            <strong>Date :</strong>
                            {{ formaterDate(audit.date_audit) }}
                        </p>

                        <p>
                            <strong>Système :</strong>
                            {{ audit.system_exploitation || "-" }}
                        </p>

                    </div>

                </div>

            </div>


            <!-- DETAILS -->

            <div
                v-if="auditSelectionne"
                class="audit-detail"
            >

                <h2>
                    Détails de l'audit
                </h2>

                <div class="detail-section">

                    <h3>Équipement</h3>

                    <p>
                        <strong>Nom :</strong>
                        {{ auditSelectionne.equipement_nom }}
                    </p>

                    <p>
                        <strong>Numéro d'inventaire :</strong>
                        {{ auditSelectionne.numero_inventaire || "-" }}
                    </p>

                </div>


                <div class="detail-section">

                    <h3>Audit</h3>

                    <p>
                        <strong>Date :</strong>
                        {{ formaterDate(auditSelectionne.date_audit) }}
                    </p>

                </div>


                <div class="detail-section">

                    <h3>Système</h3>

                    <p>
                        <strong>Système d'exploitation :</strong>
                        {{ auditSelectionne.system_exploitation || "-" }}
                    </p>

                    <p>
                        <strong>Processeur :</strong>
                        {{ auditSelectionne.processeur || "-" }}
                    </p>

                    <p>
                        <strong>Mémoire :</strong>
                        {{ auditSelectionne.memoire || "-" }}
                    </p>

                    <p>
                        <strong>Stockage :</strong>
                        {{ auditSelectionne.stockage || "-" }}
                    </p>

                    <p>
                        <strong>BIOS :</strong>
                        {{ auditSelectionne.bios || "-" }}
                    </p>

                </div>

                <div class="detail-section">

                    <h3>Données brutes</h3>

                    <button
                        type="button"
                        class="toggle-button"
                        @click="afficherDonneesBrutes = !afficherDonneesBrutes"
                    >
                        {{ afficherDonneesBrutes ? "Masquer" : "Afficher" }} les données brutes
                    </button>

                    <pre
                        v-if="afficherDonneesBrutes"
                        class="json-display"
                    >{{ formatJSON(auditSelectionne.donnees_brutes) }}</pre>

                </div>

            </div>

        </div>

    </div>
</template>


<script setup>

import { onMounted, ref } from "vue";

import {
    getRapportsAudit
} from "../services/auditService";


const audits = ref([]);

const auditsFiltres = ref([]);

const auditSelectionne = ref(null);

const chargement = ref(false);

const erreur = ref("");

const filtreEquipement = ref("");

const afficherDonneesBrutes = ref(false);

const equipementsUniques = ref([]);


async function chargerAudits() {

    chargement.value = true;

    erreur.value = "";

    try {

        audits.value = await getRapportsAudit();
        auditsFiltres.value = [...audits.value];

        // Extraire les équipements uniques pour le filtre
        equipementsUniques.value = [
            ...new Set(
                audits.value
                    .map(a => a.equipement_nom)
                    .filter(n => n)
            )
        ].sort();

        /*
         * Sélectionne automatiquement
         * le premier audit.
         */
        if (auditsFiltres.value.length > 0) {

            auditSelectionne.value =
                auditsFiltres.value[0];

        }

    } catch (error) {

        console.error(
            "Erreur lors du chargement des audits :",
            error
        );

        erreur.value =
            "Impossible de charger les rapports d'audit.";

    } finally {

        chargement.value = false;

    }
}

function filtrerAudits() {
    if (!filtreEquipement.value) {
        auditsFiltres.value = [...audits.value];
    } else {
        auditsFiltres.value = audits.value.filter(
            audit => audit.equipement_nom === filtreEquipement.value
        );
    }

    if (auditsFiltres.value.length > 0) {
        auditSelectionne.value = auditsFiltres.value[0];
    } else {
        auditSelectionne.value = null;
    }
}

function formatJSON(obj) {
    if (!obj) return "{}";
    return JSON.stringify(obj, null, 2);
}


/*
 * Sélection d'un rapport.
 */
function selectionnerAudit(audit) {

    auditSelectionne.value = audit;

}


/*
 * Transforme la date reçue par Django
 * en date lisible.
 */
function formaterDate(date) {

    if (!date) {

        return "-";

    }

    return new Date(date).toLocaleString("fr-FR");

}


onMounted(() => {

    chargerAudits();

});

</script>


<style scoped>

.audits-page {

    padding: 20px;

}


.page-header {

    display: flex;

    justify-content: space-between;

    align-items: center;

    margin-bottom: 25px;

}


.page-header h1 {

    margin-bottom: 5px;

}


.page-header p {

    margin: 0;

    color: #666;

}

.header-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.filter-select {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
}

.btn-refresh {

    padding: 10px 16px;

    border: none;

    border-radius: 6px;

    cursor: pointer;

}


.audit-layout {

    display: grid;

    grid-template-columns: 350px 1fr;

    gap: 20px;

    align-items: start;

}


.audit-list {

    display: flex;

    flex-direction: column;

    gap: 10px;

}


.audit-card {

    padding: 15px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 8px;

    cursor: pointer;

}


.audit-card:hover {

    border-color: #999;

}


.audit-card.selected {

    border-width: 2px;

}


.audit-card-header {

    display: flex;

    justify-content: space-between;

    margin-bottom: 10px;

}


.audit-card-body p {

    margin: 5px 0;

    font-size: 14px;

}


.audit-detail {

    padding: 25px;

    background: white;

    border: 1px solid #ddd;

    border-radius: 8px;

}


.audit-detail h2 {

    margin-top: 0;

}


.detail-section {

    margin-top: 20px;

    padding-bottom: 15px;

    border-bottom: 1px solid #eee;

}


.detail-section h3 {

    margin-bottom: 10px;

}


.detail-section p {

    margin: 7px 0;

}

.toggle-button {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    margin-bottom: 10px;
}

.toggle-button:hover {
    background: #f0f0f0;
}

.json-display {
    background: #f5f5f5;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    font-size: 12px;
    line-height: 1.4;
}

.message {

    padding: 30px;

    text-align: center;

}


.erreur {

    color: #b00020;

}


@media (max-width: 900px) {

    .audit-layout {

        grid-template-columns: 1fr;

    }

}

</style>