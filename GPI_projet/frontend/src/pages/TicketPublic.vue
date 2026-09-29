<template>
    <div class="page-container ticket-public-page">

        <div class="page-heading">
            <div>
                <h1 class="page-heading__title">
                    Signaler un problème
                </h1>

                <p class="page-heading__subtitle">
                    Déclarez une panne ou une réclamation sur un équipement
                    du parc
                </p>
            </div>
        </div>

        <div class="signalement-grille">

            <!-- Formulaire -->

            <section
                class="carte-formulaire"
                aria-labelledby="titre-formulaire"
            >
                <h2
                    id="titre-formulaire"
                    class="carte-formulaire__titre"
                >
                    Formulaire de signalement
                </h2>

                <p class="carte-formulaire__intro">
                    Les champs marqués d'un astérisque sont obligatoires.
                    Votre signalement sera transmis à l'équipe technique.
                </p>

                <!-- Erreur de chargement de la liste -->

                <AppAlert
                    v-if="erreurEquipements"
                    type="error"
                    :message="erreurEquipements"
                />

                <form
                    v-else
                    @submit.prevent="enregistrer"
                    novalidate
                >
                    <div class="champ">
                        <label for="equipement">
                            Équipement concerné <span aria-hidden="true">*</span>
                        </label>

                        <select
                            id="equipement"
                            v-model="equipementSelectionne"
                            :disabled="chargementEquipements || creationEnCours"
                            :aria-describedby="
                                !chargementEquipements && equipementsDisponibles.length === 0
                                    ? 'equipement-aide-indisponible'
                                    : 'equipement-aide-salle-requise'
                            "
                            required
                        >
                            <option value="">
                                {{ chargementEquipements
                                    ? 'Chargement des équipements…'
                                    : '— Sélectionner un équipement —' }}
                            </option>

                            <option
                                v-for="equipement in equipementsDisponibles"
                                :key="equipement.id"
                                :value="equipement.id"
                            >
                                {{ equipement.nom }} — {{ equipement.numero_inventaire }}
                            </option>
                        </select>

                        <p
                            v-if="!chargementEquipements && equipementsDisponibles.length === 0"
                            id="equipement-aide-indisponible"
                            class="champ__aide"
                        >
                            Aucun équipement affecté n'est disponible pour le
                            signalement.
                        </p>

                        <p
                            v-else
                            id="equipement-aide-salle-requise"
                            class="champ__aide"
                        >
                            Seuls les équipements affectés à une salle
                            peuvent être signalés.
                        </p>
                    </div>

                    <div class="champ">
                        <label for="titre">
                            Titre du problème <span aria-hidden="true">*</span>
                        </label>

                        <input
                            id="titre"
                            v-model="titre"
                            type="text"
                            placeholder="Ex. : écran noir au démarrage"
                            :disabled="creationEnCours"
                            :aria-invalid="erreurs.titre ? 'true' : 'false'"
                            aria-describedby="erreur-titre"
                            required
                        >

                        <p
                            v-if="erreurs.titre"
                            id="erreur-titre"
                            class="champ__erreur"
                        >
                            {{ erreurs.titre }}
                        </p>
                    </div>

                    <div class="champ-grille">
                        <div class="champ">
                            <label for="type">
                                Nature du problème
                            </label>

                            <select
                                id="type"
                                v-model="type"
                                :disabled="creationEnCours"
                            >
                                <option value="MAINTENANCE">
                                    Panne (maintenance)
                                </option>

                                <option value="RECLAMATION">
                                    Réclamation
                                </option>
                            </select>

                            <p class="champ__aide">
                                Panne : le matériel ne fonctionne plus.
                                Réclamation : le matériel fonctionne mais pose
                                problème.
                            </p>
                        </div>

                        <div class="champ">
                            <label for="priorite">
                                Urgence perçue
                            </label>

                            <select
                                id="priorite"
                                v-model="priorite"
                                :disabled="creationEnCours"
                            >
                                <option value="BASSE">Faible</option>
                                <option value="NORMALE">Normale</option>
                                <option value="HAUTE">Élevée</option>
                            </select>

                            <p class="champ__aide">
                                Le niveau de priorité définitif est qualifié
                                par l'administrateur.
                            </p>
                        </div>
                    </div>

                    <div class="champ">
                        <label for="description">
                            Description <span aria-hidden="true">*</span>
                        </label>

                        <textarea
                            id="description"
                            v-model="description"
                            rows="5"
                            placeholder="Décrivez ce qui se passe, depuis quand, et tout élément utile au diagnostic."
                            :disabled="creationEnCours"
                            :aria-invalid="erreurs.description ? 'true' : 'false'"
                            aria-describedby="erreur-description"
                            required
                        ></textarea>

                        <p
                            v-if="erreurs.description"
                            id="erreur-description"
                            class="champ__erreur"
                        >
                            {{ erreurs.description }}
                        </p>
                    </div>

                    <AppAlert
                        v-if="erreurCreation"
                        type="error"
                        :message="erreurCreation"
                    />

                    <AppAlert
                        v-if="succesCreation"
                        type="success"
                    >
                        <p class="succes-titre">
                            Signalement envoyé.
                        </p>

                        <p>
                            Votre demande a été transmise à l'équipe
                            technique, qui la traitera dans l'ordre des
                            priorités. Aucun suivi n'est accessible depuis
                            cette interface : contactez un administrateur
                            si vous souhaitez connaître l'avancement.
                        </p>
                    </AppAlert>

                    <div class="actions-formulaire">
                        <button
                            type="submit"
                            class="btn-primary"
                            :disabled="
                                creationEnCours
                                    || chargementEquipements
                                    || equipementsDisponibles.length === 0
                            "
                        >
                            {{ creationEnCours ? 'Envoi en cours…' : 'Envoyer le signalement' }}
                        </button>

                        <button
                            v-if="succesCreation"
                            type="button"
                            class="btn-secondary"
                            :disabled="creationEnCours"
                            @click="reinitialiser"
                        >
                            Nouveau signalement
                        </button>
                    </div>
                </form>
            </section>

            <!-- Informations -->

            <aside
                class="carte-informations"
                aria-labelledby="titre-informations"
            >
                <h2
                    id="titre-informations"
                    class="carte-informations__titre"
                >
                    Bon à savoir
                </h2>

                <section class="bloc-info">
                    <h3>Ce que vous pouvez signaler</h3>
                    <ul>
                        <li>
                            Une panne : le matériel ne fonctionne plus
                            (écran noir, impossibilité de démarrer, panne
                            réseau, etc.).
                        </li>
                        <li>
                            Une réclamation : le matériel fonctionne mais pose
                            problème (bruit inhabituel, siège endommagé,
                            recharge impossible, etc.).
                        </li>
                    </ul>
                </section>

                <section class="bloc-info">
                    <h3>Ce qui est nécessaire</h3>
                    <ul>
                        <li>L'équipement concerné.</li>
                        <li>Un titre court décrivant le problème.</li>
                        <li>Une description du symptôme.</li>
                    </ul>
                </section>

                <section class="bloc-info">
                    <h3>Après l'envoi</h3>
                    <p>
                        Le signalement est enregistré et traité par
                        l'administration, qui qualifie sa priorité et
                        organise l'intervention.
                    </p>
                    <p>
                        Vous ne pouvez ni suivre ni modifier votre signalement
                        depuis cette interface.
                    </p>
                </section>
            </aside>

        </div>

    </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue';

import { creerTicket } from '../services/ticketService';
import { getEquipementsDashboard } from '../services/dashboardService';
import { useNotificationStore } from '../stores/notifications';

import AppAlert from '../components/AppAlert.vue';

const notificationStore = useNotificationStore();

const equipements = ref([]);
const equipementSelectionne = ref("");
const titre = ref("");
const type = ref("MAINTENANCE");
const priorite = ref("NORMALE");
const description = ref("");

const chargementEquipements = ref(false);
const creationEnCours = ref(false);
const erreurCreation = ref("");
const erreurEquipements = ref("");
const succesCreation = ref(false);

/* Erreurs de validation par champ, pour afficher un message sous le
 * champ concerné plutôt qu'un message global. */
const erreurs = reactive({
    titre: "",
    description: ""
});

/*
 * Un visiteur peut déclarer une panne ou une réclamation.
 *
 * La priorité CRITIQUE n'est volontairement pas proposée : elle est
 * réservée à l'administrateur, qui qualifie le signalement via
 * l'action « qualifier ». Le formulaire resterait bloqué si l'API
 * renvoyait CRITIQUE.
 */
const equipementsDisponibles = computed(() =>
    equipements.value.filter(
        /*
         * Un équipement déjà en panne est refusé par l'API
         * ("Cet équipement est déjà en panne.") : il n'est donc pas
         * proposé, pour ne pas offrir une action qui échouerait.
         */
        (equipement) =>
            equipement.situation === "AFFECTE" &&
            equipement.etat !== "EN_PANNE"
    )
);

async function chargerEquipements() {
    chargementEquipements.value = true;
    erreurEquipements.value = "";

    try {
        equipements.value = await getEquipementsDashboard();

    } catch (error) {
        console.error(
            "Erreur lors du chargement des équipements :",
            error
        );

        erreurEquipements.value =
            "Impossible de charger la liste des équipements. Réessayez plus tard.";

    } finally {
        chargementEquipements.value = false;
    }
}

function viderErreurs() {
    erreurs.titre = "";
    erreurs.description = "";
}

/**
 * Valide les champs obligatoires côté client.
 *
 * Cette validation améliore l'ergonomie ; elle ne remplace pas les
 * contrôles de l'API, qui restent la référence.
 */
function valider() {
    viderErreurs();

    let valide = true;

    if (!equipementSelectionne.value) {
        erreurCreation.value = "Veuillez sélectionner un équipement.";
        return false;
    }

    if (!titre.value.trim()) {
        erreurs.titre = "Veuillez saisir un titre.";
        valide = false;
    }

    if (!description.value.trim()) {
        erreurs.description = "Veuillez décrire le problème rencontré.";
        valide = false;
    }

    if (!valide) {
        erreurCreation.value = "Certains champs obligatoires sont manquants.";
    }

    return valide;
}

function reinitialiser() {
    equipementSelectionne.value = "";
    titre.value = "";
    type.value = "MAINTENANCE";
    priorite.value = "NORMALE";
    description.value = "";

    succesCreation.value = false;
    erreurCreation.value = "";
    viderErreurs();
}

async function enregistrer() {
    erreurCreation.value = "";
    succesCreation.value = false;

    if (!valider()) {
        return;
    }

    creationEnCours.value = true;

    try {
        await creerTicket(
            equipementSelectionne.value,
            titre.value.trim(),
            description.value.trim(),
            type.value,
            priorite.value
        );

        notificationStore.success(
            "Signalement envoyé à l'équipe technique."
        );

        succesCreation.value = true;

        // Réinitialiser le formulaire, en conservant l'état de succès.
        equipementSelectionne.value = "";
        titre.value = "";
        type.value = "MAINTENANCE";
        priorite.value = "NORMALE";
        description.value = "";
        viderErreurs();

    } catch (error) {
        console.error(
            "Erreur lors de la création du ticket :",
            error
        );

        erreurCreation.value =
            error.response?.data?.detail ||
            "Impossible d'envoyer le signalement. Réessayez plus tard.";

        notificationStore.error(erreurCreation.value);

    } finally {
        creationEnCours.value = false;
    }
}

onMounted(() => {
    chargerEquipements();
});
</script>

<style scoped>
.ticket-public-page {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
}

.signalement-grille {
    display: grid;
    grid-template-columns: minmax(0, 1.7fr) minmax(0, 1fr);
    gap: 1.25rem;
    align-items: start;
}

/* --- Formulaire --- */

.carte-formulaire,
.carte-informations {
    padding: 1.25rem 1.4rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
}

.carte-formulaire__titre,
.carte-informations__titre {
    margin: 0 0 0.4rem;
    font-size: 1.05rem;
}

.carte-formulaire__intro {
    margin: 0 0 1.25rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.champ {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    margin-bottom: 1.05rem;
    min-width: 0;
}

.champ label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-main);
}

.champ input,
.champ select,
.champ textarea {
    width: 100%;
}

.champ__aide {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.8rem;
}

.champ__erreur {
    margin: 0;
    color: var(--danger-text);
    font-size: 0.8rem;
    font-weight: 500;
}

.champ-grille {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0 1rem;
}

.actions-formulaire {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin-top: 0.5rem;
}

.succes-titre {
    margin: 0 0 0.2rem;
    font-weight: 600;
}

/* --- Informations --- */

.bloc-info {
    margin-bottom: 1.15rem;
}

.bloc-info:last-child {
    margin-bottom: 0;
}

.bloc-info h3 {
    margin: 0 0 0.4rem;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.bloc-info ul {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

.bloc-info li {
    margin-bottom: 0.35rem;
}

.bloc-info p {
    margin: 0 0 0.5rem;
    color: var(--text-muted);
    font-size: 0.875rem;
}

@media (max-width: 900px) {
    .signalement-grille {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 640px) {
    .champ-grille {
        grid-template-columns: 1fr;
    }

    .actions-formulaire {
        flex-direction: column;
        align-items: stretch;
    }

    .actions-formulaire > * {
        justify-content: center;
        /* Cible tactile confortable sur smartphone. */
        min-height: 2.75rem;
    }
}
</style>
