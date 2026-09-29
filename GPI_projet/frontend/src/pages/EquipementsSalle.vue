<template>
    <div class="page-container equipements-salle-page">

        <!--
            Contexte hiérarchique complet : Bâtiments → Étages →
            Salles → Équipements. Le fil permet de remonter d'un cran
            à chaque niveau.
        -->

        <HierarchyContext :niveaux="hierarchie" />

        <!-- En-tête -->

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Équipements de la salle
                </h1>

                <p class="page-heading__subtitle">
                    <template v-if="salle">
                        {{ salle.nom }}
                    </template>

                    <template v-else>
                        Salle
                    </template>
                </p>
            </div>

            <div class="page-heading__actions">
                <!--
                    Libellé explicite : l'action remonte à la liste
                    des salles, pas à une page « précédente » dont le
                    sens serait ambigu.
                -->
                <router-link
                    v-if="etage"
                    :to="`/etages/${etage.id}/salles`"
                    class="btn-ghost btn-sm"
                >
                    Toutes les salles de l'étage
                </router-link>
            </div>
        </div>

        <!-- Erreur -->

        <AppAlert
            v-if="errorMessage"
            type="error"
            :message="errorMessage"
        />

        <!-- Chargement -->

        <LoadingState
            v-if="loading"
            titre="Chargement des équipements de la salle…"
        />

        <!-- Liste -->

        <template v-else-if="equipements.length > 0">
            <p class="resultats-compte">
                <span class="resultats-compte__valeur">
                    {{ equipements.length }}
                </span>
                équipement{{ equipements.length > 1 ? 's' : '' }}
                <template v-if="salle">
                    dans {{ salle.nom }}
                </template>
            </p>

            <ul class="grille-cartes equipements-liste">
                <li
                    v-for="equipement in equipements"
                    :key="equipement.id"
                >
                    <article class="carte equipement">
                        <div class="carte__entete">
                            <h2 class="carte__titre">
                                <router-link
                                    class="lien-cellule"
                                    :to="`/equipements/${equipement.id}`"
                                >
                                    {{ equipement.nom }}
                                </router-link>
                            </h2>

                            <span class="carte__meta">
                                #{{ equipement.id }}
                            </span>
                        </div>

                        <dl class="equipement__faits">
                            <div class="equipement__fait">
                                <dt>N° inventaire</dt>
                                <dd class="mono">
                                    {{ equipement.numero_inventaire }}
                                </dd>
                            </div>

                            <div class="equipement__fait">
                                <dt>Type</dt>
                                <dd>
                                    {{ libelleType(equipement.type) }}
                                </dd>
                            </div>

                            <div class="equipement__fait">
                                <dt>Fabricant</dt>
                                <dd>
                                    {{ equipement.fabricant || "Non renseigné" }}
                                </dd>
                            </div>

                            <div class="equipement__fait">
                                <dt>Modèle</dt>
                                <dd>
                                    {{ equipement.modele || "Non renseigné" }}
                                </dd>
                            </div>

                            <!--
                                Informations techniques : cette page
                                est réservée à l'administration, qui
                                reçoit ces champs du serializer.
                            -->
                            <div class="equipement__fait">
                                <dt>N° série</dt>
                                <dd class="mono">
                                    {{ equipement.numero_serie || "Non renseigné" }}
                                </dd>
                            </div>

                            <div class="equipement__fait">
                                <dt>Adresse IP</dt>
                                <dd class="mono">
                                    {{ equipement.adresse_ip || "Non renseignée" }}
                                </dd>
                            </div>

                            <div class="equipement__fait">
                                <dt>Adresse MAC</dt>
                                <dd class="mono">
                                    {{ equipement.adresse_mac || "Non renseignée" }}
                                </dd>
                            </div>
                        </dl>

                        <div class="equipement__badges">
                            <span
                                class="badge-etat"
                                :class="`etat-${equipement.etat.toLowerCase()}`"
                            >
                                {{ libelleEtat(equipement.etat) }}
                            </span>

                            <span
                                class="badge-situation"
                                :class="`situation-${equipement.situation.toLowerCase()}`"
                            >
                                {{ libelleSituation(equipement.situation) }}
                            </span>
                        </div>

                        <div class="carte__actions">
                            <router-link
                                :to="`/equipements/${equipement.id}`"
                                class="btn-secondary btn-sm"
                            >
                                Voir la fiche
                            </router-link>
                        </div>
                    </article>
                </li>
            </ul>
        </template>

        <!-- Aucun équipement -->

        <EmptyState
            v-else-if="!errorMessage"
            titre="Aucun équipement dans cette salle"
            message="Aucun matériel n'est affecté à cette salle. Affectez un équipement depuis sa fiche, ou choisissez une autre salle."
        >
            <router-link
                v-if="etage"
                :to="`/etages/${etage.id}/salles`"
                class="btn-secondary btn-sm"
            >
                Revenir aux salles de l'étage
            </router-link>
        </EmptyState>

    </div>
</template>

<script setup>
/**
 * Équipements affectés à une salle.
 *
 * La page se place au dernier niveau de la hiérarchie du parc : le
 * fil de contexte reste affiché afin que l'administrateur sache
 * toujours dans quel bâtiment, étage et salle il se trouve, et puisse
 * remonter d'un cran à tout moment.
 *
 * Les informations techniques (n° de série, adresses réseau) ne sont
 * affichées que dans cet espace d'administration, qui reçoit le
 * serializer complet.
 */
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";

import { getSalle } from "../services/salleService";
import { getEtage } from "../services/etageService";
import { getBatiment } from "../services/batimentService";
import { getEquipementsParSalle } from "../services/equipementService";

import AppAlert from "../components/AppAlert.vue";
import EmptyState from "../components/EmptyState.vue";
import HierarchyContext from "../components/HierarchyContext.vue";
import LoadingState from "../components/LoadingState.vue";

const route = useRoute();

// Données
const salle = ref(null);
const etage = ref(null);
const batiment = ref(null);
const equipements = ref([]);

const loading = ref(false);
const errorMessage = ref("");

const salleId = computed(() => route.params.salleId);

/*
 * Libellés lisibles des champs techniques.
 *
 * Ces tables reprennent les choix déclarés par le modèle Django. Une
 * valeur inconnue reste affichée telle quelle plutôt que masquée.
 */
const LIBELLES_TYPE = {
    ORDINATEUR: "Ordinateur",
};

const LIBELLES_ETAT = {
    EN_SERVICE: "En service",
    EN_PANNE: "En panne",
    EN_MAINTENANCE: "En maintenance",
    HORS_SERVICE: "Hors service",
};

const LIBELLES_SITUATION = {
    AFFECTE: "Affecté",
    EN_STOCK: "En stock",
};

function libelleType(type) {
    return LIBELLES_TYPE[type] || type || "—";
}

function libelleEtat(etat) {
    return LIBELLES_ETAT[etat] || etat || "—";
}

function libelleSituation(situation) {
    return LIBELLES_SITUATION[situation] || situation || "—";
}

/*
 * Le modèle autorise un nom d'étage vide : l'affichage retombait
 * alors sur une chaîne vide.
 */
function libelleNom(etage) {
    if (!etage) {
        return "Étage";
    }

    return etage.nom || `Étage n°${etage.numero}`;
}

/*
 * Fil de hiérarchie Bâtiments → Étages → Salles → Équipements.
 * Chaque niveau mène à sa page ; le dernier est la page courante.
 */
const hierarchie = computed(() => [
    {
        cle: 'batiments',
        libelle: 'Bâtiments',
        lien: '/batiments',
    },
    {
        cle: 'batiment',
        libelle: batiment.value?.nom,
        lien: batiment.value
            ? `/batiments/${batiment.value.id}/etages`
            : null,
    },
    {
        cle: 'etage',
        libelle: etage.value ? libelleNom(etage.value) : 'Étage',
        lien: etage.value
            ? `/etages/${etage.value.id}/salles`
            : null,
    },
    {
        cle: 'salle',
        libelle: salle.value?.nom || 'Salle',
        lien: salle.value
            ? `/salles/${salle.value.id}/equipements`
            : null,
    },
    {
        cle: 'equipements',
        libelle: 'Équipements',
    },
]);

// Charger la salle et ses équipements
async function chargerDonnees() {
    loading.value = true;
    errorMessage.value = "";

    try {
        // Récupérer les informations de la salle
        salle.value = await getSalle(salleId.value);

        /*
         * L'étage et le bâtiment ne sont pas nécessaires pour charger
         * les équipements : si ces appels échouent, la liste reste
         * affichée et le fil se limite aux niveaux connus.
         */
        if (salle.value?.etage) {
            try {
                etage.value = await getEtage(salle.value.etage);

                if (etage.value?.batiment) {
                    batiment.value = await getBatiment(etage.value.batiment);
                }

            } catch (erreurContexte) {
                console.error(
                    "Erreur lors du chargement du contexte :",
                    erreurContexte
                );
            }
        }

        // Récupérer les équipements de cette salle
        equipements.value = await getEquipementsParSalle(salleId.value);

    } catch (error) {
        console.error(error);

        errorMessage.value = "Impossible de charger les équipements.";

    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    chargerDonnees();
});
</script>

<style scoped>
.equipements-salle-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Les équipements portent une fiche plus riche : deux colonnes. */
.equipements-liste {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.equipements-liste > li {
    display: flex;
}

.equipement {
    width: 100%;
}

.lien-cellule {
    font-weight: 600;
    color: var(--primary);
}

.equipement__faits {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.6rem 1rem;
    margin: 0;
    padding: 0.75rem 0;
    border-top: 1px solid var(--border-light);
    border-bottom: 1px solid var(--border-light);
}

.equipement__fait {
    min-width: 0;
}

.equipement__fait dt {
    color: var(--text-light);
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.equipement__fait dd {
    margin: 0.15rem 0 0;
    color: var(--text-main);
    font-size: 0.875rem;
    font-weight: 500;
    word-break: break-word;
}

.equipement__badges {
    display: flex;
    flex-wrap: wrap;
    gap: 0.35rem;
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.8125rem;
}
</style>
