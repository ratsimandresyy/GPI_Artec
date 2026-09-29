<template>
    <div class="page-container plan-public-page">

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Plans du système
                </h1>

                <p class="page-heading__subtitle">
                    Localisation graphique des équipements, par bâtiment
                    et par étage
                </p>
            </div>

            <div class="page-heading__actions">
                <router-link
                    to="/signaler"
                    class="btn-primary btn-sm"
                >
                    Signaler un problème
                </router-link>
            </div>
        </div>

        <!-- Chargement -->

        <LoadingState
            v-if="loading"
            titre="Chargement des plans…"
        />

        <!-- Erreur -->

        <AppAlert
            v-else-if="errorMessage"
            type="error"
            :message="errorMessage"
        />

        <template v-else>
            <!-- Sélecteurs -->

            <div class="selecteurs">
                <div class="selecteur">
                    <label for="batiment-select">
                        Bâtiment
                    </label>

                    <select
                        id="batiment-select"
                        v-model="batimentSelectionne"
                        @change="changerBatiment"
                    >
                        <option value="">
                            — Choisir un bâtiment —
                        </option>

                        <option
                            v-for="batiment in batiments"
                            :key="batiment.id"
                            :value="batiment.id"
                        >
                            {{ batiment.nom }}
                        </option>
                    </select>
                </div>

                <div class="selecteur">
                    <label for="etage-select">
                        Étage
                    </label>

                    <select
                        id="etage-select"
                        v-model="etageSelectionne"
                        :disabled="!batimentSelectionne"
                        @change="changerEtage"
                    >
                        <option value="">
                            — Choisir un étage —
                        </option>

                        <option
                            v-for="etage in etagesFiltres"
                            :key="etage.id"
                            :value="etage.id"
                        >
                            {{ etage.nom }}
                        </option>
                    </select>
                </div>

                <div class="selecteur">
                    <label for="plan-select">
                        Plan
                    </label>

                    <select
                        id="plan-select"
                        v-model="planSelectionne"
                        :disabled="!etageSelectionne"
                    >
                        <option value="">
                            — Choisir un plan —
                        </option>

                        <option
                            v-for="plan in plansFiltres"
                            :key="plan.id"
                            :value="plan.id"
                        >
                            {{ libellePlan(plan) }}
                        </option>
                    </select>
                </div>
            </div>

            <!-- Plan sélectionné -->

            <section
                v-if="planSelectionneObjet"
                class="plan-zone"
                aria-labelledby="titre-plan"
            >
                <div class="plan-contexte">
                    <h2
                        id="titre-plan"
                        class="plan-contexte__titre"
                    >
                        {{ contextePlan.titre }}
                    </h2>

                    <p class="plan-contexte__legende">
                        {{ contextePlan.legende }}
                    </p>
                </div>

                <p
                    v-if="equipementsPlan.length > 0"
                    class="plan-contexte__compteur"
                >
                    {{ equipementsPlan.length }} équipement(s) positionné(s)
                    sur ce plan
                </p>

                <p
                    v-else
                    class="plan-contexte__compteur text-muted"
                >
                    Aucun équipement positionné sur ce plan.
                </p>
            </section>

            <EmptyState
                v-if="!planSelectionne"
                titre="Aucun plan sélectionné"
                message="Choisissez un bâtiment, puis un étage et un plan pour afficher la localisation des équipements."
            />

            <div
                v-else
                class="plan-visualisation"
            >
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

            <!-- Aide de lecture -->

            <p
                v-if="planSelectionne"
                class="plan-aide"
            >
                Cliquez sur un équipement du plan pour consulter ses
                informations, ou utilisez la liste des équipements pour y
                accéder directement.
            </p>
        </template>

        <!-- Fiche équipement -->

        <div
            v-if="equipementSelectionne"
            class="modal-overlay"
            @click.self="fermerModal"
        >
            <div
                class="modal"
                role="dialog"
                aria-modal="true"
                :aria-label="`Fiche de l'équipement ${equipementSelectionne.nom}`"
            >
                <div class="modal-entete">
                    <h2>{{ equipementSelectionne.nom }}</h2>

                    <button
                        type="button"
                        class="modal-fermeture"
                        aria-label="Fermer la fiche"
                        @click="fermerModal"
                    >
                        <span aria-hidden="true">×</span>
                    </button>
                </div>

                <dl class="modal-liste">
                    <div class="modal-ligne">
                        <dt>Type</dt>
                        <dd>{{ equipementSelectionne.type }}</dd>
                    </div>

                    <div class="modal-ligne">
                        <dt>N° inventaire</dt>
                        <dd>
                            <span class="mono">
                                {{ equipementSelectionne.numero_inventaire }}
                            </span>
                        </dd>
                    </div>

                    <div class="modal-ligne">
                        <dt>Fabricant</dt>
                        <dd>{{ equipementSelectionne.fabricant || "—" }}</dd>
                    </div>

                    <div class="modal-ligne">
                        <dt>Modèle</dt>
                        <dd>{{ equipementSelectionne.modele || "—" }}</dd>
                    </div>

                    <div class="modal-ligne">
                        <dt>État</dt>
                        <dd>
                            <span :class="`etat-${equipementSelectionne.etat.toLowerCase()}`">
                                {{ libelleEtat(equipementSelectionne.etat) }}
                            </span>
                        </dd>
                    </div>

                    <div class="modal-ligne">
                        <dt>Situation</dt>
                        <dd>
                            <span :class="`situation-${equipementSelectionne.situation.toLowerCase()}`">
                                {{ libelleSituation(equipementSelectionne.situation) }}
                            </span>
                        </dd>
                    </div>
                </dl>

                <div class="modal-actions">
                    <router-link
                        :to="`/equipements/${equipementSelectionne.id}`"
                        class="btn-primary btn-sm"
                        @click="fermerModal"
                    >
                        Voir la fiche complète
                    </router-link>

                    <button
                        type="button"
                        class="btn-secondary btn-sm"
                        @click="fermerModal"
                    >
                        Fermer
                    </button>
                </div>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

import { getBatiments } from '../services/batimentService';
import { getEtages } from '../services/etageService';
import { getSalles } from '../services/salleService';
import {
    getPlans,
    getPositions
} from '../services/localisationService';
import { getEquipementsDashboard } from '../services/dashboardService';

import AppAlert from '../components/AppAlert.vue';
import EmptyState from '../components/EmptyState.vue';
import LoadingState from '../components/LoadingState.vue';
import PlanViewer from '../components/PlanViewer.vue';

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
const planSelectionne = ref("");

const loading = ref(true);
const errorMessage = ref("");

/* Libellés lisibles des champs techniques */
const LIBELLES_ETAT = {
    EN_SERVICE: 'En service',
    EN_PANNE: 'En panne',
    EN_MAINTENANCE: 'En maintenance',
    HORS_SERVICE: 'Hors service',
};

const LIBELLES_SITUATION = {
    AFFECTE: 'Affecté',
    EN_STOCK: 'En stock',
};

function libelleEtat(etat) {
    return LIBELLES_ETAT[etat] || etat || '—';
}

function libelleSituation(situation) {
    return LIBELLES_SITUATION[situation] || situation || '—';
}

// Computed pour filtrer les étages selon le bâtiment
const etagesFiltres = computed(() => {
    if (!batimentSelectionne.value) return [];
    return etages.value.filter(etage => String(etage.batiment) === String(batimentSelectionne.value));
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

/*
 * Libellé d'un plan.
 *
 * Le modèle `Plan` n'expose aucun champ `nom` : le libellé est
 * reconstruit à partir de l'étage rattaché, exactement comme le fait
 * déjà `PlanViewer.vue`. Aucune donnée n'est inventée.
 */
function libellePlan(plan) {
    if (!plan) {
        return '';
    }

    const etage = etages.value.find(
        (item) => String(item.id) === String(plan.etage)
    );

    if (etage?.nom) {
        return `Plan — ${etage.nom}`;
    }

    return 'Plan du bâtiment';
}

/*
 * Contexte lisible du plan affiché : bâtiment, étage et nom du plan.
 * Aucune donnée n'est inventée : chaque libellé provient des
 * référentiels déjà chargés.
 */
const contextePlan = computed(() => {
    const plan = planSelectionneObjet.value;

    if (!plan) {
        return { titre: '', legende: '' };
    }

    const etage = etages.value.find(
        (item) => String(item.id) === String(plan.etage)
    );

    const batiment = etage
        ? batiments.value.find(
            (item) => String(item.id) === String(etage.batiment)
        )
        : null;

    return {
        titre: libellePlan(plan),
        legende: [
            batiment ? batiment.nom : null,
            etage ? etage.nom : null
        ]
            .filter(Boolean)
            .join(' · ') || 'Aucun bâtiment associé'
    };
});

/*
 * Équipements positionnés sur le plan affiché, pour le compteur.
 *
 * Le décompte est purement informatif : il ne modifie ni les positions
 * ni le comportement de PlanViewer.
 */
const equipementsPlan = computed(() => {
    const plan = planSelectionneObjet.value;

    if (!plan) return [];

    const idsPositions = new Set(
        positions.value
            .filter((position) => String(position.plan) === String(plan.id))
            .map((position) => String(position.equipement))
    );

    return equipements.value.filter(
        (equipement) => idsPositions.has(String(equipement.id))
    );
});

async function chargerDonnees() {
    loading.value = true;
    errorMessage.value = "";

    try {
        const [donneesBatiments, donneesEtages, donneesSalles, donneesPlans, donneesEquipements, donneesPositions] =
            await Promise.all([
                getBatiments(),
                getEtages(),
                getSalles(),
                getPlans(),
                getEquipementsDashboard(),
                getPositions()
            ]);

        batiments.value = donneesBatiments;
        etages.value = donneesEtages;
        salles.value = donneesSalles;
        plans.value = donneesPlans;
        equipements.value = donneesEquipements;
        positions.value = donneesPositions;

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
        errorMessage.value =
            "Impossible de charger les plans. Vérifiez votre connexion puis réessayez.";

    } finally {
        loading.value = false;
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
    planSelectionne.value = "";
}

function changerEtage() {
    planSelectionne.value = "";
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
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

/* --- Sélecteurs --- */

.selecteurs {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.85rem;
    padding: 1.1rem 1.25rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
}

.selecteur {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    min-width: 0;
}

.selecteur label {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
}

.selecteur select {
    width: 100%;
}

/* --- Contexte du plan --- */

.plan-zone {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 0.5rem 1rem;
}

.plan-contexte__titre {
    margin: 0;
    font-size: 1.1rem;
}

.plan-contexte__legende {
    margin: 0.15rem 0 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}

.plan-contexte__compteur {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text-muted);
}

.plan-visualisation {
    min-width: 0;
}

.plan-aide {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.85rem;
}

/* --- Fiche équipement (modale) --- */

.modal-entete {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 0.9rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border-light);
}

.modal-entete h2 {
    margin: 0;
    font-size: 1.2rem;
}

.modal-fermeture {
    flex-shrink: 0;
    width: 2rem;
    height: 2rem;
    padding: 0;
    background-color: transparent;
    color: var(--text-muted);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    font-size: 1.1rem;
    line-height: 1;
}

.modal-fermeture:hover {
    background-color: var(--bg-subtle);
    color: var(--text-main);
}

.modal-liste {
    margin: 0;
}

.modal-ligne {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-light);
}

.modal-ligne:last-child {
    border-bottom: none;
}

.modal-ligne dt {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.modal-ligne dd {
    margin: 0;
    text-align: right;
    font-weight: 500;
}

.modal-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.1rem;
    padding-top: 0.9rem;
    border-top: 1px solid var(--border-light);
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.875em;
}

@media (max-width: 640px) {
    .modal-ligne {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.15rem;
    }

    .modal-ligne dd {
        text-align: left;
    }

    .modal-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .modal-actions > * {
        justify-content: center;
    }
}
</style>
