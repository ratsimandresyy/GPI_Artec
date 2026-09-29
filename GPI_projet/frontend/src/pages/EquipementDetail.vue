<template>
    <div class="page-container equipement-detail-page">

        <!-- Retour à la liste -->

        <router-link
            to="/equipements"
            class="btn-ghost btn-sm retour-liste"
        >
            <span aria-hidden="true">←</span>
            Retour à la liste des équipements
        </router-link>

        <!-- Chargement -->

        <LoadingState
            v-if="loading"
            titre="Chargement de la fiche équipement…"
        />

        <!-- Erreur -->

        <AppAlert
            v-else-if="errorMessage"
            type="error"
        >
            <p class="erreur-titre">
                {{ erreurTitre }}
            </p>

            <p>{{ errorMessage }}</p>

            <router-link
                to="/equipements"
                class="btn-secondary btn-sm"
            >
                Revenir à la liste
            </router-link>
        </AppAlert>

        <!-- Fiche -->

        <template v-else-if="equipement">
            <div class="page-heading">
                <div>
                    <h1 class="page-heading__title">
                        {{ equipement.nom }}
                    </h1>

                    <p class="page-heading__subtitle">
                        {{ libelleType(equipement.type) }}
                        <span aria-hidden="true">·</span>
                        N° d'inventaire {{ equipement.numero_inventaire }}
                    </p>
                </div>

                <div class="page-heading__actions">
                    <router-link
                        v-if="equipement.salle"
                        to="/plan"
                        class="btn-secondary btn-sm"
                    >
                        Voir sur le plan
                    </router-link>

                    <button
                        v-if="estAdmin"
                        type="button"
                        class="btn-delete btn-sm"
                        @click="demanderSuppression"
                    >
                        Supprimer
                    </button>
                </div>
            </div>

            <p
                v-if="!estAdmin"
                class="mention-visiteur"
            >
                Consultation en lecture seule. Les informations techniques
                d'inventaire et de réseau sont réservées à l'administration.
            </p>

            <!--
                Résumé opérationnel : état et situation sont les deux
                informations qui décident d'une intervention. Elles
                sont placées au-dessus des fiches pour être lues sans
                parcourir la page.
            -->
            <section
                class="carte-resume"
                aria-labelledby="titre-resume"
            >
                <h2
                    id="titre-resume"
                    class="carte-resume__titre visually-hidden"
                >
                    Résumé
                </h2>

                <div class="carte-resume__item">
                    <span class="carte-resume__cle">
                        État
                    </span>

                    <span
                        class="badge-etat"
                        :class="`etat-${equipement.etat.toLowerCase()}`"
                    >
                        {{ libelleEtat(equipement.etat) }}
                    </span>
                </div>

                <div class="carte-resume__item">
                    <span class="carte-resume__cle">
                        Situation
                    </span>

                    <span
                        class="badge-situation"
                        :class="`situation-${equipement.situation.toLowerCase()}`"
                    >
                        {{ libelleSituation(equipement.situation) }}
                    </span>
                </div>

                <div class="carte-resume__item">
                    <span class="carte-resume__cle">
                        Localisation
                    </span>

                    <span class="carte-resume__valeur">
                        {{ localisation.batiment }} · {{ localisation.etage }} · {{ localisation.salle }}
                    </span>
                </div>
            </section>

            <div class="grille-fiches">

                <!-- Identification -->

                <section
                    class="fiche"
                    aria-labelledby="titre-identification"
                >
                    <h2
                        id="titre-identification"
                        class="fiche__titre"
                    >
                        Identification
                    </h2>

                    <dl class="fiche__liste">
                        <div class="fiche__ligne">
                            <dt>Nom</dt>
                            <dd>{{ equipement.nom }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Type</dt>
                            <dd>{{ libelleType(equipement.type) }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Fabricant</dt>
                            <dd>{{ equipement.fabricant || "—" }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Modèle</dt>
                            <dd>{{ equipement.modele || "—" }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>N° d'inventaire</dt>
                            <dd class="mono">
                                {{ equipement.numero_inventaire }}
                            </dd>
                        </div>

                        <!--
                            Le numéro de série n'est pas exposé au
                            visiteur : il n'apparaît que pour
                            l'administration.
                        -->
                        <div
                            v-if="estAdmin"
                            class="fiche__ligne"
                        >
                            <dt>N° de série</dt>
                            <dd class="mono">
                                {{ equipement.numero_serie || "—" }}
                            </dd>
                        </div>
                    </dl>
                </section>

                <!-- Localisation -->

                <section
                    class="fiche"
                    aria-labelledby="titre-localisation"
                >
                    <h2
                        id="titre-localisation"
                        class="fiche__titre"
                    >
                        Localisation
                    </h2>

                    <dl class="fiche__liste">
                        <div class="fiche__ligne">
                            <dt>Bâtiment</dt>
                            <dd>{{ localisation.batiment }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Étage</dt>
                            <dd>{{ localisation.etage }}</dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Salle</dt>
                            <dd>{{ localisation.salle }}</dd>
                        </div>
                    </dl>

                    <p
                        v-if="!equipement.salle"
                        class="fiche__note"
                    >
                        Cet équipement n'est pas rattaché à une salle : il
                        n'apparaît donc sur aucun plan.
                    </p>

                    <router-link
                        v-else
                        to="/plan"
                        class="btn-secondary btn-sm fiche__action"
                    >
                        Localiser sur le plan
                    </router-link>
                </section>

                <!-- État -->

                <section
                    class="fiche"
                    aria-labelledby="titre-etat"
                >
                    <h2
                        id="titre-etat"
                        class="fiche__titre"
                    >
                        État et situation
                    </h2>

                    <dl class="fiche__liste">
                        <div class="fiche__ligne">
                            <dt>État</dt>

                            <dd>
                                <span
                                    class="badge-etat"
                                    :class="`etat-${equipement.etat.toLowerCase()}`"
                                >
                                    {{ libelleEtat(equipement.etat) }}
                                </span>
                            </dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Situation dans le parc</dt>

                            <dd>
                                <span
                                    class="badge-situation"
                                    :class="`situation-${equipement.situation.toLowerCase()}`"
                                >
                                    {{ libelleSituation(equipement.situation) }}
                                </span>
                            </dd>
                        </div>

                        <p class="fiche__explication">
                            L'état décrit le fonctionnement du matériel ; la
                            situation décrit sa place dans le parc. Les deux
                            se combinent : un matériel en panne peut être
                            affecté comme en stock.
                        </p>

                        <div
                            v-if="estAdmin && equipement.condition_stock"
                            class="fiche__ligne"
                        >
                            <dt>Condition du stock</dt>
                            <dd>
                                {{ libelleConditionStock(equipement.condition_stock) }}
                            </dd>
                        </div>
                    </dl>
                </section>

                <!-- Réseau (administration uniquement) -->

                <section
                    v-if="estAdmin"
                    class="fiche"
                    aria-labelledby="titre-reseau"
                >
                    <h2
                        id="titre-reseau"
                        class="fiche__titre"
                    >
                        Réseau
                    </h2>

                    <dl class="fiche__liste">
                        <div class="fiche__ligne">
                            <dt>Adresse IP</dt>
                            <dd class="mono">
                                {{ equipement.adresse_ip || "—" }}
                            </dd>
                        </div>

                        <div class="fiche__ligne">
                            <dt>Adresse MAC</dt>
                            <dd class="mono">
                                {{ equipement.adresse_mac || "—" }}
                            </dd>
                        </div>
                    </dl>

                    <p
                        v-if="!equipement.adresse_ip && !equipement.adresse_mac"
                        class="fiche__note"
                    >
                        Aucune information réseau n'est renseignée pour
                        cet équipement.
                    </p>
                </section>

            </div>
        </template>

        <!-- Confirmation de suppression -->

        <ConfirmDialog
            v-if="suppressionDemandee && estAdmin"
            titre="Supprimer cet équipement ?"
            :message="`L'équipement « ${equipement.nom} » sera définitivement supprimé du parc.`"
            consequence="Cette action est irréversible. L'historique des signalements associés à cet équipement sera également perdu."
            @confirm="supprimer"
            @cancel="suppressionDemandee = false"
        />

    </div>
</template>

<script setup>
/**
 * Fiche d'un équipement.
 *
 * La présentation est organisée par nature d'information :
 * identification, localisation, état, puis réseau. Les sections
 * réservées à l'administration (numéro de série, adresse IP, adresse
 * MAC, condition de stock) ne sont jamais rendues pour un visiteur,
 * et le serializer public ne les transmet pas davantage.
 *
 * Aucune donnée n'est ajoutée ici : la fiche affiche uniquement ce que
 * l'API fournit, résolu en libellés lisibles.
 */
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";
import {
    getEquipement,
    supprimerEquipement
} from "../services/equipementService";
import { getBatiments } from "../services/batimentService";
import { getEtages } from "../services/etageService";
import { getSalles } from "../services/salleService";

import AppAlert from "../components/AppAlert.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import LoadingState from "../components/LoadingState.vue";

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const equipement = ref(null);
const salles = ref([]);
const batiments = ref([]);
const etages = ref([]);

const loading = ref(false);
const errorMessage = ref("");
const introuvable = ref(false);
const suppressionDemandee = ref(false);

const estAdmin = computed(() => authStore.isAdmin);

/*
 * Libellés lisibles : la classe CSS conserve la valeur brute pour le
 * contraste visuel, le texte affiché reste compréhensible. Ces tables
 * reprennent les choix déclarés par le modèle Django ; une valeur
 * inconnue reste affichée telle quelle.
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

const LIBELLES_CONDITION_STOCK = {
    NEUF: "Neuf",
    OCCASION: "Occasion",
    RECONDITIONNE: "Reconditionné",
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

function libelleConditionStock(condition) {
    return LIBELLES_CONDITION_STOCK[condition] || condition || "—";
}

/*
 * L'API renvoie `salle` sous forme d'identifiant. Pour présenter une
 * localisation lisible (bâtiment / étage / salle), on résout la
 * hiérarchie à partir des référentiels déjà exposés publiquement.
 */
const localisation = computed(() => {
    const salleId = equipement.value?.salle;

    if (!salleId) {
        return { batiment: "—", etage: "—", salle: "Non affecté" };
    }

    const salle = salles.value.find(
        (item) => String(item.id) === String(salleId)
    );

    if (!salle) {
        return { batiment: "—", etage: "—", salle: `Salle ${salleId}` };
    }

    const etage = etages.value.find(
        (item) => String(item.id) === String(salle.etage)
    );

    const batiment = etages.value.length && batiments.value.length
        ? batiments.value.find(
            (item) =>
                etage && String(item.id) === String(etage.batiment)
        )
        : null;

    return {
        batiment: batiment ? batiment.nom : "—",
        etage: etage ? etage.nom : "—",
        salle: salle.nom,
    };
});

const erreurTitre = computed(() =>
    introuvable.value
        ? "Équipement introuvable"
        : "Chargement impossible"
);

const id = route.params.id;

async function chargerReferentiels() {
    try {
        const [donneesSalles, donneesEtages, donneesBatiments] =
            await Promise.all([
                getSalles(),
                getEtages(),
                getBatiments(),
            ]);

        salles.value = donneesSalles;
        etages.value = donneesEtages;
        batiments.value = donneesBatiments;

    } catch (error) {
        /*
         * La localisation reste affichée avec les identifiants bruts
         * si les référentiels sont indisponibles : la fiche principale
         * n'est pas bloquée par cet appel secondaire.
         */
        console.error(
            "Erreur lors du chargement des référentiels :", error
        );
    }
}

async function chargerEquipement() {
    loading.value = true;
    errorMessage.value = "";
    introuvable.value = false;

    try {
        equipement.value = await getEquipement(id);
        await chargerReferentiels();

    } catch (error) {
        introuvable.value = error.response?.status === 404;

        errorMessage.value = introuvable.value
            ? `Aucun équipement ne correspond à l'identifiant ${id}.`
            : "Impossible de charger cet équipement. Vérifiez votre connexion puis réessayez.";

    } finally {
        loading.value = false;
    }
}

/*
 * Suppression : action réservée à l'administration.
 * L'API reste seule juge de l'autorisation effective.
 */
function demanderSuppression() {
    suppressionDemandee.value = true;
}

async function supprimer() {
    try {
        await supprimerEquipement(id);
        suppressionDemandee.value = false;
        router.push("/equipements");

    } catch (error) {
        suppressionDemandee.value = false;

        errorMessage.value =
            error.response?.data?.detail ||
            "Impossible de supprimer l'équipement.";
    }
}

onMounted(() => {
    chargerEquipement();
});
</script>

<style scoped>
.equipement-detail-page {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.retour-liste {
    align-self: flex-start;
}

.mention-visiteur {
    margin: 0;
    padding: 0.7rem 0.9rem;
    background-color: var(--info-light);
    color: var(--info-text);
    border: 1px solid var(--info-border);
    border-radius: var(--radius-md);
    font-size: 0.875rem;
}

.erreur-titre {
    margin: 0 0 0.25rem;
    font-weight: 600;
}

.erreur-titre + p {
    margin: 0 0 0.6rem;
}

/* Résumé opérationnel */

.carte-resume {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem 1.75rem;
    padding: 0.9rem 1.15rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.carte-resume__item {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 0.3rem;
    min-width: 0;
}

.carte-resume__cle {
    color: var(--text-light);
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.carte-resume__valeur {
    color: var(--text-main);
    font-size: 0.875rem;
    font-weight: 500;
}

.grille-fiches {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    align-items: start;
}

.fiche {
    padding: 1.15rem 1.25rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
}

.fiche__titre {
    margin: 0 0 0.9rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid var(--border-light);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.fiche__liste {
    margin: 0;
}

.fiche__ligne {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border-light);
}

.fiche__ligne:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.fiche__ligne dt {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.fiche__ligne dd {
    margin: 0;
    text-align: right;
    font-weight: 500;
}

.fiche__explication {
    margin: 0.6rem 0 0;
    color: var(--text-muted);
    font-size: 0.8125rem;
    line-height: 1.45;
}

.fiche__note {
    margin: 0.9rem 0 0;
    padding: 0.7rem 0.85rem;
    background-color: var(--bg-subtle);
    border-radius: var(--radius-md);
    color: var(--text-muted);
    font-size: 0.85rem;
}

.fiche__action {
    margin-top: 0.9rem;
}

.mono {
    font-family: var(--font-mono);
    font-size: 0.875em;
}

@media (max-width: 640px) {
    .grille-fiches {
        grid-template-columns: 1fr;
    }

    .fiche__ligne {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.15rem;
    }

    .fiche__ligne dd {
        text-align: left;
    }
}
</style>
