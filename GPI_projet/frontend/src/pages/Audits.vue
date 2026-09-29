<template>
    <div class="page-container audits-page">

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Audits WinAudit
                </h1>

                <p class="page-heading__subtitle">
                    Informations collectées automatiquement sur les
                    équipements du parc.
                </p>
            </div>

            <div class="page-heading__actions">
                <button
                    type="button"
                    class="btn-secondary btn-sm"
                    :disabled="chargement"
                    @click="chargerAudits"
                >
                    Actualiser
                </button>
            </div>
        </div>

        <!-- Erreur -->

        <AppAlert
            v-if="erreur"
            type="error"
            :message="erreur"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="chargement"
            titre="Chargement des rapports d'audit…"
        />

        <template v-else-if="!erreur">
            <!--
                Résumé : les quatre indicateurs sont dérivés des
                rapports déjà chargés. Aucun appel supplémentaire et
                aucun indicateur qui ne soit pas présent dans la
                réponse de l'API.
            -->

            <section
                class="statistiques"
                aria-label="Situation des imports"
            >
                <div class="statistique">
                    <span class="statistique__intitule">
                        Rapports collectés
                    </span>

                    <span class="statistique__valeur">
                        {{ audits.length }}
                    </span>
                </div>

                <div class="statistique">
                    <span class="statistique__intitule">
                        Équipements couverts
                    </span>

                    <span class="statistique__valeur">
                        {{ equipementsUniques.length }}
                    </span>
                </div>

                <div class="statistique">
                    <span class="statistique__intitule">
                        Dernière collecte
                    </span>

                    <span class="statistique__valeur-statistique">
                        {{ formaterDateCourte(derniereCollecte) }}
                    </span>
                </div>

                <!--
                    L'API n'expose aucun statut d'import : on ne peut
                    donc que compter les rapports dont les données
                    système sont absentes, sans en déduire un échec.
                -->
                <div
                    class="statistique"
                    :class="{ 'statistique--alerte': rapportsIncomplets > 0 }"
                >
                    <span class="statistique__intitule">
                        Sans donnée système
                    </span>

                    <span class="statistique__valeur">
                        {{ rapportsIncomplets }}
                    </span>
                </div>
            </section>

            <!-- Aucun rapport -->

            <EmptyState
                v-if="audits.length === 0"
                titre="Aucun rapport d'audit"
                message="Aucun rapport WinAudit n'a encore été collecté. Les rapports apparaissent dès qu'un poste est analysé par le service d'import."
            />

            <!-- Aucun résultat après filtrage -->

            <EmptyState
                v-else-if="auditsFiltres.length === 0"
                titre="Aucun rapport pour cet équipement"
                message="Aucun rapport n'a été collecté pour l'équipement sélectionné."
            >
                <button
                    type="button"
                    class="btn-secondary btn-sm"
                    @click="filtreEquipement = ''; filtrerAudits()"
                >
                    Afficher tous les équipements
                </button>
            </EmptyState>

            <!-- Liste et détail -->

            <div
                v-else
                class="audit-layout"
            >
                <!-- Liste -->

                <section
                    class="audit-liste-panneau"
                    aria-labelledby="titre-liste-audits"
                >
                    <h2
                        id="titre-liste-audits"
                        class="panneau__titre"
                    >
                        Rapports
                    </h2>

                    <!--
                        Le filtre porte sur l'équipement concerné, seul
                        critère réellement disponible dans la réponse.
                    -->
                    <div class="audit-filtre">
                        <label for="audit-filtre-equipement">
                            Équipement
                        </label>

                        <select
                            id="audit-filtre-equipement"
                            v-model="filtreEquipement"
                            @change="filtrerAudits"
                        >
                            <option value="">
                                Tous les équipements
                            </option>

                            <option
                                v-for="equipement in equipementsUniques"
                                :key="equipement"
                                :value="equipement"
                            >
                                {{ equipement }}
                            </option>
                        </select>
                    </div>

                    <!--
                        La liste est une liste de boutons : chaque
                        rapport est ainsi atteignable au clavier, ce
                        qu'un bloc cliquable ne permettait pas.
                    -->
                    <ul class="audit-liste">
                        <li
                            v-for="audit in auditsFiltres"
                            :key="audit.id"
                        >
                            <button
                                type="button"
                                class="audit-carte"
                                :class="{
                                    'audit-carte--selectionne':
                                        auditSelectionne?.id === audit.id,
                                }"
                                :aria-pressed="auditSelectionne?.id === audit.id"
                                @click="selectionnerAudit(audit)"
                            >
                                <span class="audit-carte__entete">
                                    <span class="audit-carte__nom">
                                        {{
                                            audit.equipement_nom
                                                || 'Équipement non rattaché'
                                        }}
                                    </span>

                                    <span class="audit-carte__id">
                                        #{{ audit.id }}
                                    </span>
                                </span>

                                <span class="audit-carte__faits">
                                    <span class="audit-carte__fait">
                                        N° inventaire
                                        <span class="mono">
                                            {{ audit.numero_inventaire || "—" }}
                                        </span>
                                    </span>

                                    <span class="audit-carte__fait">
                                        {{ formaterDate(audit.date_audit) }}
                                    </span>
                                </span>
                            </button>
                        </li>
                    </ul>
                </section>

                <!-- Détail -->

                <section
                    class="audit-detail"
                    aria-labelledby="titre-detail-audit"
                    aria-live="polite"
                >
                    <h2
                        id="titre-detail-audit"
                        class="panneau__titre"
                    >
                        Détails du rapport
                    </h2>

                    <template v-if="auditSelectionne">
                        <div class="detail-section">
                            <h3>Équipement</h3>

                            <dl class="detail-liste">
                                <div class="detail-liste__ligne">
                                    <dt>Nom</dt>
                                    <dd>
                                        {{
                                            auditSelectionne.equipement_nom
                                                || 'Équipement non rattaché'
                                        }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>Numéro d'inventaire</dt>
                                    <dd class="mono">
                                        {{ auditSelectionne.numero_inventaire || "—" }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>Date du rapport</dt>
                                    <dd>
                                        {{ formaterDate(auditSelectionne.date_audit) }}
                                    </dd>
                                </div>
                            </dl>
                        </div>

                        <div class="detail-section">
                            <h3>Système</h3>

                            <dl class="detail-liste">
                                <div class="detail-liste__ligne">
                                    <dt>Système d'exploitation</dt>
                                    <dd>
                                        {{ auditSelectionne.system_exploitation || "—" }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>Processeur</dt>
                                    <dd>
                                        {{ auditSelectionne.processeur || "—" }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>Mémoire</dt>
                                    <dd>
                                        {{ auditSelectionne.memoire || "—" }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>Stockage</dt>
                                    <dd>
                                        {{ auditSelectionne.stockage || "—" }}
                                    </dd>
                                </div>

                                <div class="detail-liste__ligne">
                                    <dt>BIOS</dt>
                                    <dd>
                                        {{ auditSelectionne.bios || "—" }}
                                    </dd>
                                </div>
                            </dl>
                        </div>

                        <div class="detail-section">
                            <h3>Données brutes</h3>

                            <button
                                type="button"
                                class="btn-ghost btn-sm"
                                :aria-expanded="afficherDonneesBrutes ? 'true' : 'false'"
                                aria-controls="audit-donnees-brutes"
                                @click="afficherDonneesBrutes = !afficherDonneesBrutes"
                            >
                                {{
                                    afficherDonneesBrutes
                                        ? 'Masquer les données brutes'
                                        : 'Afficher les données brutes'
                                }}
                            </button>

                            <pre
                                v-if="afficherDonneesBrutes"
                                id="audit-donnees-brutes"
                                class="json-display"
                            >{{ formatJSON(auditSelectionne.donnees_brutes) }}</pre>
                        </div>
                    </template>

                    <p
                        v-else
                        class="text-muted"
                    >
                        Sélectionnez un rapport pour afficher son détail.
                    </p>
                </section>
            </div>
        </template>

    </div>
</template>

<script setup>
/**
 * Suivi des imports WinAudit.
 *
 * Cette page est un simple consumer des rapports déjà collectés par
 * le pipeline d'import. Elle n'intervient ni dans la collecte, ni dans
 * la déduplication par identifiant matériel, ni dans la surveillance du
 * dossier serveur : ce sont des.backend.
 *
 * Aucun indicateur n'est inventé : les compteurs affichés sont tous
 * dérivés des champs réellement renvoyés par l'API
 * (`date_audit`, `equipement_nom`, `system_exploitation`).
 */
import { computed, onMounted, ref } from "vue";

import { getRapportsAudit } from "../services/auditService";

import AppAlert from "../components/AppAlert.vue";
import EmptyState from "../components/EmptyState.vue";
import LoadingState from "../components/LoadingState.vue";

const audits = ref([]);
const auditsFiltres = ref([]);
const auditSelectionne = ref(null);

const chargement = ref(false);
const erreur = ref("");

const filtreEquipement = ref("");

const afficherDonneesBrutes = ref(false);

const equipementsUniques = ref([]);

// --------------------------------------------------
// Indicateurs
// --------------------------------------------------

/*
 * Date de collecte la plus récente. L'API ne fournit pas de date
 * d'import distincte : c'est la date portée par le rapport qui sert
 * de repère.
 */
const derniereCollecte = computed(() => {
    if (audits.value.length === 0) {
        return null;
    }

    return audits.value.reduce(
        (plusRecente, audit) =>
            !plusRecente ||
            new Date(audit.date_audit) > new Date(plusRecente)
                ? audit.date_audit
                : plusRecente,
        null
    );
});

/*
 * Rapports dépourvus de donnée système. L'API n'expose aucun statut
 * d'import : ce compte mesure une information manquante, pas un échec
 * de l'import.
 */
const rapportsIncomplets = computed(
    () => audits.value.filter(
        (audit) => !audit.system_exploitation
    ).length
);

// --------------------------------------------------
// Chargement
// --------------------------------------------------

async function chargerAudits() {
    chargement.value = true;
    erreur.value = "";

    try {
        audits.value = await getRapportsAudit();
        auditsFiltres.value = [...audits.value];

        /*
         * Le filtre est remis à zéro avec la liste : le conserver
         * laisserait le sélecteur afficher un critère qui ne filtre
         * plus rien.
         */
        filtreEquipement.value = "";

        // Extraire les équipements uniques pour le filtre
        equipementsUniques.value = [
            ...new Set(
                audits.value
                    .map((a) => a.equipement_nom)
                    .filter((n) => n)
            ),
        ].sort();

        /*
         * Sélectionne automatiquement le premier audit, comme
         * auparavant.
         */
        if (auditsFiltres.value.length > 0) {
            auditSelectionne.value = auditsFiltres.value[0];
        } else {
            auditSelectionne.value = null;
        }
    } catch (error) {
        console.error(
            "Erreur lors du chargement des audits :",
            error
        );

        erreur.value = "Impossible de charger les rapports d'audit.";
    } finally {
        chargement.value = false;
    }
}

function filtrerAudits() {
    if (!filtreEquipement.value) {
        auditsFiltres.value = [...audits.value];
    } else {
        auditsFiltres.value = audits.value.filter(
            (audit) => audit.equipement_nom === filtreEquipement.value
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

    /*
     * Les données brutes concernaient le rapport précédent : on les
     * masque pour ne pas afficher un contenu qui ne correspond plus à
     * la sélection.
     */
    afficherDonneesBrutes.value = false;
}

/*
 * Transforme la date reçue par Django en date lisible.
 */
function formaterDate(date) {
    if (!date) {
        return "—";
    }

    return new Date(date).toLocaleString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

/*
 * Format court pour la tuile de résumé, où la place est comptée.
 */
function formaterDateCourte(date) {
    if (!date) {
        return "—";
    }

    return new Date(date).toLocaleDateString("fr-FR", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
    });
}

onMounted(() => {
    chargerAudits();
});
</script>

<style scoped>
.audits-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* La tuile « dernière collecte » porte une date, pas un nombre :
   elle ne doit donc pas hériter de la grande taille chiffrée. */
.statistique__valeur-statistique {
    color: var(--text-main);
    font-size: 1.05rem;
    font-weight: 700;
    line-height: 1.5;
}

.audit-layout {
    display: grid;
    grid-template-columns: minmax(300px, 380px) 1fr;
    gap: 1rem;
    align-items: start;
}

.audit-liste-panneau,
.audit-detail {
    padding: 1rem 1.15rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.panneau__titre {
    margin: 0 0 0.85rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border-light);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* Filtre */

.audit-filtre {
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    margin-bottom: 0.85rem;
}

.audit-filtre label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-muted);
}

/* Liste */

.audit-liste {
    max-height: 32rem;
    overflow-y: auto;
    margin: 0;
    padding: 0;
    list-style: none;
}

.audit-liste > li + li {
    margin-top: 0.4rem;
}

.audit-carte {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: 100%;
    padding: 0.65rem 0.75rem;
    text-align: left;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.audit-carte:hover {
    background-color: var(--bg-subtle);
    border-color: var(--border-medium);
}

/* La sélection est portée par la bordure ET l'état `aria-pressed` :
   jamais par la seule couleur. */
.audit-carte--selectionne {
    background-color: var(--primary-light);
    border-color: var(--primary);
}

.audit-carte__entete {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
}

.audit-carte__nom {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-main);
}

.audit-carte__id {
    flex-shrink: 0;
    color: var(--text-light);
    font-family: var(--font-mono);
    font-size: 0.75rem;
}

.audit-carte__faits {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 0.75rem;
    color: var(--text-muted);
    font-size: 0.75rem;
}

.audit-carte__fait {
    display: inline-flex;
    gap: 0.25rem;
}

/* Détail */

.detail-section {
    padding-bottom: 0.9rem;
    margin-bottom: 0.9rem;
    border-bottom: 1px solid var(--border-light);
}

.detail-section:last-of-type {
    padding-bottom: 0;
    margin-bottom: 0;
    border-bottom: none;
}

.detail-section h3 {
    margin: 0 0 0.6rem;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.detail-liste {
    margin: 0;
}

.detail-liste__ligne {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--border-light);
}

.detail-liste__ligne:last-child {
    border-bottom: none;
}

.detail-liste__ligne dt {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.detail-liste__ligne dd {
    margin: 0;
    text-align: right;
    font-weight: 500;
    word-break: break-word;
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.875em;
}

.json-display {
    margin: 0.6rem 0 0;
    padding: 0.85rem;
    background-color: var(--bg-subtle);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    overflow-x: auto;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    line-height: 1.5;
    max-height: 22rem;
}

@media (max-width: 900px) {
    .audit-layout {
        grid-template-columns: 1fr;
    }

    .audit-liste {
        max-height: 20rem;
    }
}

@media (max-width: 640px) {
    .statistiques {
        grid-template-columns: 1fr 1fr;
    }

    .detail-liste__ligne {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.15rem;
    }

    .detail-liste__ligne dd {
        text-align: left;
    }
}
</style>
