<template>
    <div
        class="modal-overlay"
        @click.self="demanderFermeture"
    >
        <div
            ref="boite"
            class="modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="titre-formulaire-equipement"
            tabindex="-1"
        >
            <h2
                id="titre-formulaire-equipement"
                class="formulaire__titre"
            >
                {{ mode === 'creation' ? 'Nouvel équipement' : 'Modifier l\'équipement' }}
            </h2>

            <p class="formulaire__legende">
                Les champs marqués d'un astérisque sont obligatoires.
            </p>

            <!--
                Erreur globale : elle vient de l'API et n'est jamais
                remplacée par un texte générique. Le backend reste
                l'autorité de la validation.
            -->
            <p
                v-if="erreurs.detail"
                class="formulaire__erreur"
                role="alert"
            >
                {{ erreurs.detail }}
            </p>

            <form @submit.prevent="enregistrer">
                <!-- Identification -->

                <fieldset class="formulaire__groupe">
                    <legend class="formulaire__groupe-titre">
                        Identification
                    </legend>

                    <div class="form-group">
                        <label for="equipement-nom">
                            Nom
                            <span class="requis" aria-hidden="true">*</span>
                        </label>

                        <input
                            id="equipement-nom"
                            v-model="formulaire.nom"
                            type="text"
                            required
                            :disabled="chargement"
                            :aria-invalid="Boolean(erreurs.nom)"
                            :class="{ 'champ-obligatoire': erreurs.nom }"
                            :aria-describedby="erreurs.nom ? 'equipement-nom-erreur' : undefined"
                            placeholder="Ex : PC-ADMIN-01"
                        >

                        <p
                            v-if="erreurs.nom"
                            id="equipement-nom-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.nom }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="equipement-type">
                            Type
                            <span class="requis" aria-hidden="true">*</span>
                        </label>

                        <select
                            id="equipement-type"
                            v-model="formulaire.type"
                            required
                            :disabled="chargement"
                        >
                            <option value="ORDINATEUR">Ordinateur</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="equipement-numero-inventaire">
                            N° inventaire
                            <span class="requis" aria-hidden="true">*</span>
                        </label>

                        <input
                            id="equipement-numero-inventaire"
                            v-model="formulaire.numero_inventaire"
                            type="text"
                            required
                            :disabled="chargement"
                            :aria-invalid="Boolean(erreurs.numero_inventaire)"
                            :class="{ 'champ-obligatoire': erreurs.numero_inventaire }"
                            :aria-describedby="erreurs.numero_inventaire ? 'equipement-numero-inventaire-erreur' : undefined"
                            placeholder="Ex : INV-2024-001"
                        >

                        <p
                            v-if="erreurs.numero_inventaire"
                            id="equipement-numero-inventaire-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.numero_inventaire }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="equipement-numero-serie">
                            N° série
                        </label>

                        <input
                            id="equipement-numero-serie"
                            v-model="formulaire.numero_serie"
                            type="text"
                            :disabled="chargement"
                            :aria-invalid="Boolean(erreurs.numero_serie)"
                            :class="{ 'champ-obligatoire': erreurs.numero_serie }"
                            :aria-describedby="erreurs.numero_serie ? 'equipement-numero-serie-erreur' : undefined"
                            placeholder="Ex : SN-123456789"
                        >

                        <p
                            v-if="erreurs.numero_serie"
                            id="equipement-numero-serie-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.numero_serie }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="equipement-fabricant">
                            Fabricant
                        </label>

                        <input
                            id="equipement-fabricant"
                            v-model="formulaire.fabricant"
                            type="text"
                            :disabled="chargement"
                            placeholder="Ex : Dell, HP, Lenovo…"
                        >
                    </div>

                    <div class="form-group">
                        <label for="equipement-modele">
                            Modèle
                        </label>

                        <input
                            id="equipement-modele"
                            v-model="formulaire.modele"
                            type="text"
                            :disabled="chargement"
                            placeholder="Ex : Latitude 7420"
                        >
                    </div>
                </fieldset>

                <!-- Réseau -->

                <fieldset class="formulaire__groupe">
                    <legend class="formulaire__groupe-titre">
                        Réseau
                    </legend>

                    <div class="form-group">
                        <label for="equipement-adresse-ip">
                            Adresse IP
                        </label>

                        <input
                            id="equipement-adresse-ip"
                            v-model="formulaire.adresse_ip"
                            type="text"
                            :disabled="chargement"
                            :aria-invalid="Boolean(erreurs.adresse_ip)"
                            :class="{ 'champ-obligatoire': erreurs.adresse_ip }"
                            :aria-describedby="erreurs.adresse_ip ? 'equipement-adresse-ip-erreur' : undefined"
                            placeholder="Ex : 192.168.1.100"
                        >

                        <p
                            v-if="erreurs.adresse_ip"
                            id="equipement-adresse-ip-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.adresse_ip }}
                        </p>
                    </div>

                    <div class="form-group">
                        <label for="equipement-adresse-mac">
                            Adresse MAC
                        </label>

                        <input
                            id="equipement-adresse-mac"
                            v-model="formulaire.adresse_mac"
                            type="text"
                            :disabled="chargement"
                            placeholder="Ex : 00:1A:2B:3C:4D:5E"
                        >
                    </div>
                </fieldset>

                <!-- État et situation -->

                <fieldset class="formulaire__groupe">
                    <legend class="formulaire__groupe-titre">
                        État et situation
                    </legend>

                    <p class="formulaire__aide">
                        L'état décrit le fonctionnement du matériel, la
                        situation sa place dans le parc. Les deux se
                        combinent.
                    </p>

                    <div class="form-group">
                        <label for="equipement-etat">
                            État
                        </label>

                        <select
                            id="equipement-etat"
                            v-model="formulaire.etat"
                            :disabled="chargement"
                        >
                            <option value="EN_SERVICE">En service</option>
                            <option value="EN_PANNE">En panne</option>
                            <option value="EN_MAINTENANCE">En maintenance</option>
                            <option value="HORS_SERVICE">Hors service</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="equipement-situation">
                            Situation
                        </label>

                        <select
                            id="equipement-situation"
                            v-model="formulaire.situation"
                            :disabled="chargement"
                            @change="changerSituation"
                        >
                            <option value="AFFECTE">Affecté</option>
                            <option value="EN_STOCK">En stock</option>
                        </select>
                    </div>

                    <!--
                        La condition de stock est exigée par l'API
                        lorsque la situation est EN_STOCK : le champ
                        apparaît dans ce cas uniquement.
                    -->
                    <div
                        v-if="formulaire.situation === 'EN_STOCK'"
                        class="form-group"
                    >
                        <label for="equipement-condition-stock">
                            Condition du stock
                            <span class="requis" aria-hidden="true">*</span>
                        </label>

                        <select
                            id="equipement-condition-stock"
                            v-model="formulaire.condition_stock"
                            required
                            :disabled="chargement"
                            :aria-invalid="Boolean(erreurs.condition_stock)"
                            :class="{ 'champ-obligatoire': erreurs.condition_stock }"
                            :aria-describedby="erreurs.condition_stock ? 'equipement-condition-stock-erreur' : undefined"
                        >
                            <option value="NEUF">Neuf</option>
                            <option value="OCCASION">Occasion</option>
                            <option value="RECONDITIONNE">Reconditionné</option>
                        </select>

                        <p
                            v-if="erreurs.condition_stock"
                            id="equipement-condition-stock-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.condition_stock }}
                        </p>
                    </div>

                    <div
                        v-if="formulaire.situation === 'AFFECTE'"
                        class="form-group"
                    >
                        <label for="equipement-salle">
                            Salle
                        </label>

                        <select
                            id="equipement-salle"
                            v-model="formulaire.salle"
                            :disabled="chargement || chargementSalles"
                            :aria-invalid="Boolean(erreurs.salle)"
                            :class="{ 'champ-obligatoire': erreurs.salle }"
                            :aria-describedby="erreurs.salle ? 'equipement-salle-erreur' : undefined"
                        >
                            <option value="">Aucune salle</option>

                            <option
                                v-for="salle in salles"
                                :key="salle.id"
                                :value="salle.id"
                            >
                                {{ salle.nom }}
                            </option>
                        </select>

                        <p
                            v-if="erreurs.salle"
                            id="equipement-salle-erreur"
                            class="champ-erreur"
                        >
                            {{ erreurs.salle }}
                        </p>
                    </div>
                </fieldset>

                <div class="formulaire__actions">
                    <button
                        type="button"
                        class="btn-secondary"
                        :disabled="chargement"
                        @click="$emit('close')"
                    >
                        Annuler
                    </button>

                    <button
                        type="submit"
                        class="btn-primary"
                        :disabled="chargement"
                    >
                        {{ chargement ? 'Enregistrement…' : 'Enregistrer' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
/**
 * Formulaire de création et de modification d'un équipement.
 *
 * Le composant ne valide rien : la préparation des valeurs et les
 * règles métier appartiennent à l'API, dont les messages d'erreur
 * sont transmis tels quels par la page.
 *
 * `chargement` est piloté par la page, qui attend réellement la
 * réponse de l'API. Il ne peut pas être déduit du seul `emit` : celui-ci
 * est synchrone et se terminerait avant l'écriture.
 */
import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
import { getSalles } from '../services/salleService';
import { useFocusTrap } from '../composables/useFocusTrap';

const props = defineProps({
    mode: {
        type: String,
        default: 'creation'
    },

    equipement: {
        type: Object,
        default: null
    },

    // Vrai pendant l'appel d'enregistrement effectué par la page.
    chargement: {
        type: Boolean,
        default: false
    },

    // Erreurs renvoyées par l'API, indexées par nom de champ.
    erreurs: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['close', 'save']);

const formulaire = ref(creerFormulaireVide());
const salles = ref([]);
const chargementSalles = ref(false);
const boite = ref(null);

/*
 * Le focus entre dans la boîte et y reste prisonnier. `tabindex="-1"`
 * rend la boîte programmable sans l'ajouter à l'ordre de tabulation :
 * le focus initial porte sur la boîte entière, pas sur le premier champ,
 * pour que l'utilisateur entende d'abord le titre du formulaire.
 */
useFocusTrap(boite, { focusInitial: 'conteneur' });

function creerFormulaireVide() {
    return {
        nom: '',
        type: 'ORDINATEUR',
        numero_inventaire: '',
        numero_serie: '',
        fabricant: '',
        modele: '',
        adresse_ip: '',
        adresse_mac: '',
        etat: 'EN_SERVICE',
        situation: 'AFFECTE',
        condition_stock: '',
        salle: ''
    };
}

async function chargerSalles() {
    chargementSalles.value = true;

    try {
        salles.value = await getSalles();

    } catch (error) {
        // La liste des salles est un confort, pas un prérequis : sa
        // liste déroulante reste vide et l'utilisateur peut conserver
        // une affectation existante.
        console.error('Erreur lors du chargement des salles:', error);

    } finally {
        chargementSalles.value = false;
    }
}

function changerSituation() {
    if (formulaire.value.situation === 'AFFECTE') {
        formulaire.value.condition_stock = '';
    } else {
        formulaire.value.salle = '';

        // Définir une valeur par défaut pour condition_stock
        if (!formulaire.value.condition_stock) {
            formulaire.value.condition_stock = 'NEUF';
        }
    }
}

function enregistrer() {
    emit('save', { ...formulaire.value });
}

function demanderFermeture() {
    if (!props.chargement) {
        emit('close');
    }
}

/*
 * Échap ferme la modale.
 *
 * L'écoute est portée par `document` et non par la boîte : celle-ci
 * n'était pas focusable, si bien que son `@keydown.esc` ne se
 * déclenchait que si le focus se trouvait déjà dans le formulaire.
 * L'écouteur global rend la fermeture fiable quel que soit le lieu
 * du focus, comme dans `ConfirmDialog.vue` et `Tickets.vue`.
 *
 * `demanderFermeture` filtre elle-même l'état de chargement.
 */
function surTouche(event) {
    if (event.key === 'Escape') {
        demanderFermeture();
    }
}

watch(() => props.equipement, (nouvelEquipement) => {
    if (!nouvelEquipement) {
        formulaire.value = creerFormulaireVide();
        return;
    }

    formulaire.value = {
        nom: nouvelEquipement.nom || '',
        type: nouvelEquipement.type || 'ORDINATEUR',
        numero_inventaire: nouvelEquipement.numero_inventaire || '',
        numero_serie: nouvelEquipement.numero_serie || '',
        fabricant: nouvelEquipement.fabricant || '',
        modele: nouvelEquipement.modele || '',
        adresse_ip: nouvelEquipement.adresse_ip || '',
        adresse_mac: nouvelEquipement.adresse_mac || '',
        etat: nouvelEquipement.etat || 'EN_SERVICE',
        situation: nouvelEquipement.situation || 'AFFECTE',
        condition_stock: nouvelEquipement.condition_stock || '',
        salle: nouvelEquipement.salle || ''
    };
}, { immediate: true });

onMounted(() => {
    chargerSalles();

    document.addEventListener('keydown', surTouche);
});

onBeforeUnmount(() => {
    document.removeEventListener('keydown', surTouche);
});
</script>

<style scoped>
.modal-overlay {
    z-index: 1000;
    padding: 1.5rem;
}

.modal {
    width: 100%;
    max-width: 640px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 1.5rem;
}

/*
 * `fieldset` apporte un cadre par défaut qu'il faut neutraliser avant
 * d'appliquer la présentation des groupes du design system.
 */
.formulaire__groupe {
    margin: 0 0 1rem;
    padding: 0 0 0.25rem;
    border: none;
    border-bottom: 1px solid var(--border-light);
}

.formulaire__groupe:last-of-type {
    margin-bottom: 0;
    border-bottom: none;
}

.formulaire__aide {
    margin: 0 0 0.85rem;
    color: var(--text-muted);
    font-size: 0.8125rem;
}

.formulaire__erreur {
    margin: 0 0 1rem;
    padding: 0.65rem 0.8rem;
    background-color: var(--danger-light);
    border: 1px solid rgba(220, 38, 38, 0.25);
    border-radius: var(--radius-md);
    color: var(--danger-text);
    font-size: 0.875rem;
}
</style>
