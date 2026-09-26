<template>
    <div class="equipements-page">
        <div class="page-header">
            <div>
                <h1>Équipements</h1>
                <p>Gestion du parc informatique</p>
            </div>

            <div class="header-actions">
                <button
                    v-if="!estAdmin"
                    type="button"
                    class="secondary-button"
                    @click="retourDashboard"
                >
                    ← Retour au dashboard
                </button>

                <button
                    v-if="estAdmin"
                    type="button"
                    class="primary-button"
                    @click="ouvrirCreation"
                >
                    + Nouvel équipement
                </button>
            </div>
        </div>

        <!-- Filtres (uniquement pour admin) -->
        <Filters
            v-if="estAdmin"
            :filters="filterConfig"
            :initial-filters="filters"
            @change="setFilters"
            @reset="resetFilters"
        />

        <!-- Message info pour visiteurs -->
        <p v-if="!estAdmin" class="visitor-info">
            Mode visiteur : Vous pouvez consulter la liste des équipements et voir leur localisation sur le plan.
        </p>

        <!--Chargement-->
        <p v-if="loading">
            Chargement des équipements...
        </p>

        <!--Erreur-->
        <p v-else-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>

        <!-- Aucun resultat -->
         <p v-else-if="filteredItems.length === 0">
            Aucun équipement trouvé.
         </p>

        <!-- Tableau Admin -->
         <table v-else-if="estAdmin">
            <thead>
                <tr>
                    <TableSort
                        key="id"
                        label="ID"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="nom"
                        label="Nom"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="type"
                        label="Type"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="numero_inventaire"
                        label="N° inventaire"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="fabricant"
                        label="Fabricant"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="modele"
                        label="Modèle"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="adresse_ip"
                        label="Adresse IP"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="etat"
                        label="État"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <TableSort
                        key="situation"
                        label="Situation"
                        :current-sort-key="sortKey"
                        :current-sort-order="sortOrder"
                        @sort="setSort"
                    />
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr
                v-for="equipement in paginatedItems"
                :key="equipement.id"
                >
                    <td>{{ equipement.id }}</td>
                    <td><button type="button" class="equipement-link" @click="voirEquipement(equipement.id)">{{ equipement.nom }}</button></td>
                    <td>{{ equipement.type }}</td>
                    <td>{{ equipement.numero_inventaire }}</td>
                    <td>{{ equipement.fabricant || "-" }}</td>
                    <td>{{ equipement.modele || "-" }}</td>
                    <td>{{ equipement.adresse_ip || "-" }}</td>
                    <td><span :class="`etat-${equipement.etat.toLowerCase()}`">{{ equipement.etat }}</span></td>
                    <td><span :class="`situation-${equipement.situation.toLowerCase()}`">{{ equipement.situation }}</span></td>
                    <td>
                        <button
                            type="button"
                            class="action-button"
                            @click="ouvrirModification(equipement)"
                        >
                            Modifier
                        </button>
                        <button
                            type="button"
                            class="action-button danger"
                            @click="supprimer(equipement)"
                        >
                            Supprimer
                        </button>
                    </td>
                </tr>
            </tbody>
         </table>

        <!-- Tableau Visiteur -->
         <table v-else class="visitor-table">
            <thead>
                <tr>
                    <th>Nom</th>
                    <th>Type</th>
                    <th>N° inventaire</th>
                    <th>Localisation</th>
                    <th>Actions</th>
                </tr>
            </thead>

            <tbody>
                <tr
                v-for="equipement in filteredItems"
                :key="equipement.id"
                >
                    <td>{{ equipement.nom }}</td>
                    <td>{{ equipement.type }}</td>
                    <td>{{ equipement.numero_inventaire }}</td>
                    <td>{{ equipement.salle?.nom || "Non affecté" }}</td>
                    <td>
                        <button
                            v-if="equipement.salle"
                            type="button"
                            class="action-button primary"
                            @click="voirSurPlan(equipement)"
                        >
                            📍 Voir sur le plan
                        </button>
                        <span v-else class="no-location">Non positionné</span>
                    </td>
                </tr>
            </tbody>
         </table>

        <!-- Pagination (uniquement pour admin) -->
        <Pagination
            v-if="estAdmin && filteredItems.length > 0"
            :current-page="currentPage"
            :page-size="pageSize"
            :total-items="filteredItems.length"
            @change="setPage"
            @page-size-change="setPageSize"
        />

        <!-- Modal formulaire -->
        <EquipementForm
            v-if="afficherFormulaire"
            :mode="modeFormulaire"
            :equipement="equipementSelectionne"
            @close="fermerFormulaire"
            @save="enregistrer"
        />
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getEquipements, creerEquipement, modifierEquipement, supprimerEquipement } from '../services/equipementService';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useNotificationStore } from '../stores/notifications';
import EquipementForm from '../components/EquipementForm.vue';
import Pagination from '../components/Pagination.vue';
import Filters from '../components/Filters.vue';
import TableSort from '../components/TableSort.vue';
import { useTableData } from '../composables/useTableData';

const router = useRouter();
const authStore = useAuthStore();
const notificationStore = useNotificationStore();

const equipements = ref([]);
const loading = ref(false);
const errorMessage = ref("");

const afficherFormulaire = ref(false);
const modeFormulaire = ref("creation");
const equipementSelectionne = ref(null);

const estAdmin = computed(() => authStore.isAdmin);

// Configuration des filtres (uniquement pour admin)
const filterConfig = computed(() => {
    if (!estAdmin.value) {
        return [];
    }

    return [
        { key: 'etat', label: 'État', type: 'select', options: [
            { value: 'EN_SERVICE', label: 'En service' },
            { value: 'EN_PANNE', label: 'En panne' },
            { value: 'EN_MAINTENANCE', label: 'En maintenance' },
            { value: 'HORS_SERVICE', label: 'Hors service' }
        ]},
        { key: 'situation', label: 'Situation', type: 'select', options: [
            { value: 'AFFECTE', label: 'Affecté' },
            { value: 'EN_STOCK', label: 'En stock' }
        ]},
        { key: 'type', label: 'Type', type: 'select', options: [
            { value: 'ORDINATEUR', label: 'Ordinateur' }
        ]}
    ];
});

// Utilisation du composable pour pagination/filtrage/tri
const {
    currentPage,
    pageSize,
    sortKey,
    sortOrder,
    filters,
    filteredItems,
    paginatedItems,
    totalPages,
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

async function chargerEquipements() {
    loading.value = true;
    errorMessage.value = "";

    try {
        equipements.value = await getEquipements();
    } catch (error) {
        console.error(
            "Erreur lors du chargement des équipements :", error
        );

        errorMessage.value =
            "Impossible de charger les équipements.";
    } finally {
        loading.value = false;
    }
}

function voirEquipement(id) {
    console.log("Équipement sélectionné :", id);
    router.push(`/equipements/${id}`);
}

function ouvrirCreation() {
    modeFormulaire.value = "creation";
    equipementSelectionne.value = null;
    afficherFormulaire.value = true;
}

function ouvrirModification(equipement) {
    modeFormulaire.value = "modification";
    equipementSelectionne.value = equipement;
    afficherFormulaire.value = true;
}

function fermerFormulaire() {
    afficherFormulaire.value = false;
    equipementSelectionne.value = null;
}

function retourDashboard() {
    router.push('/dashboard-public');
}

function voirSurPlan(equipement) {
    router.push({
        path: '/plan',
        query: { equipementId: equipement.id }
    });
}


async function enregistrer(donnees) {
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
        const errorMsg = error.response?.data?.detail || error.response?.data || "Impossible d'enregistrer l'équipement.";
        errorMessage.value = errorMsg;
        notificationStore.error(errorMsg);
        // Ne pas fermer le formulaire en cas d'erreur
    }
}

async function supprimer(equipement) {
    const confirmation = window.confirm(
        `Voulez-vous vraiment supprimer l'équipement "${equipement.nom}" ?`
    );

    if (!confirmation) {
        return;
    }

    try {
        await supprimerEquipement(equipement.id);
        notificationStore.success("Équipement supprimé avec succès");
        await chargerEquipements();
    } catch (error) {
        console.error("Erreur lors de la suppression:", error);
        errorMessage.value = error.response?.data?.detail || "Impossible de supprimer l'équipement.";
        notificationStore.error(errorMessage.value);
    }
}

onMounted(() => {
    chargerEquipements();
});
</script>

<style scoped>
.equipements-page {
    padding: 30px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.header-actions {
    display: flex;
    gap: 10px;
}

.page-header h1 {
    margin: 0;
    font-size: 28px;
}

.page-header p {
    margin: 5px 0 0;
    color: #666;
}

.primary-button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background: #222;
    color: white;
    cursor: pointer;
}

.secondary-button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    background: #eee;
    color: #333;
    cursor: pointer;
}

.visitor-info {
    background: #e7f3ff;
    border: 1px solid #b8daff;
    border-radius: 6px;
    padding: 12px;
    margin-bottom: 20px;
    color: #004085;
    font-size: 14px;
}

.visitor-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.visitor-table th,
.visitor-table td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

.visitor-table th {
    font-weight: bold;
    background: #f8f8f8;
}

.no-location {
    color: #999;
    font-style: italic;
}

.equipement-link {
    border: none;
    background: none;
    padding: 0;
    cursor: pointer;
    text-decoration: underline;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

th,
td {
    border: 1px solid #ddd;
    padding: 10px;
    text-align: left;
}

th {
    font-weight: bold;
}

.error {
    color: red;
}

.action-button {
    padding: 5px 10px;
    margin-right: 5px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.action-button.danger {
    background: #dc3545;
    color: white;
}

.action-button.primary {
    background: #28a745;
    color: white;
}

.action-button:not(.danger):not(.primary) {
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
