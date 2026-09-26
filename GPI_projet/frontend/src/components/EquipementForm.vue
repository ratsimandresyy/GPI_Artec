<template>
    <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal">
            <h2>
                {{ mode === 'creation' ? 'Nouvel équipement' : 'Modifier l\'équipement' }}
            </h2>

            <form @submit.prevent="enregistrer">
                <div class="form-group">
                    <label for="nom">Nom *</label>
                    <input
                        id="nom"
                        v-model="formulaire.nom"
                        type="text"
                        required
                        placeholder="Ex: PC-ADMIN-01"
                    >
                </div>

                <div class="form-group">
                    <label for="type">Type *</label>
                    <select
                        id="type"
                        v-model="formulaire.type"
                        required
                    >
                        <option value="ORDINATEUR">Ordinateur</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="numero_inventaire">N° inventaire *</label>
                    <input
                        id="numero_inventaire"
                        v-model="formulaire.numero_inventaire"
                        type="text"
                        required
                        placeholder="Ex: INV-2024-001"
                    >
                </div>

                <div class="form-group">
                    <label for="numero_serie">N° série</label>
                    <input
                        id="numero_serie"
                        v-model="formulaire.numero_serie"
                        type="text"
                        placeholder="Ex: SN-123456789"
                    >
                </div>

                <div class="form-group">
                    <label for="fabricant">Fabricant</label>
                    <input
                        id="fabricant"
                        v-model="formulaire.fabricant"
                        type="text"
                        placeholder="Ex: Dell, HP, Lenovo..."
                    >
                </div>

                <div class="form-group">
                    <label for="modele">Modèle</label>
                    <input
                        id="modele"
                        v-model="formulaire.modele"
                        type="text"
                        placeholder="Ex: Latitude 7420"
                    >
                </div>

                <div class="form-group">
                    <label for="adresse_ip">Adresse IP</label>
                    <input
                        id="adresse_ip"
                        v-model="formulaire.adresse_ip"
                        type="text"
                        placeholder="Ex: 192.168.1.100"
                    >
                </div>

                <div class="form-group">
                    <label for="adresse_mac">Adresse MAC</label>
                    <input
                        id="adresse_mac"
                        v-model="formulaire.adresse_mac"
                        type="text"
                        placeholder="Ex: 00:1A:2B:3C:4D:5E"
                    >
                </div>

                <div class="form-group">
                    <label for="etat">État</label>
                    <select
                        id="etat"
                        v-model="formulaire.etat"
                    >
                        <option value="EN_SERVICE">En service</option>
                        <option value="EN_PANNE">En panne</option>
                        <option value="EN_MAINTENANCE">En maintenance</option>
                        <option value="HORS_SERVICE">Hors service</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="situation">Situation</label>
                    <select
                        id="situation"
                        v-model="formulaire.situation"
                        @change="changerSituation"
                    >
                        <option value="AFFECTE">Affecté</option>
                        <option value="EN_STOCK">En stock</option>
                    </select>
                </div>

                <div class="form-group" v-if="formulaire.situation === 'EN_STOCK'">
                    <label for="condition_stock">Condition du stock *</label>
                    <select
                        id="condition_stock"
                        v-model="formulaire.condition_stock"
                        required
                    >
                        <option value="NEUF">Neuf</option>
                        <option value="OCCASION">Occasion</option>
                        <option value="RECONDITIONNE">Reconditionné</option>
                    </select>
                </div>

                <div class="form-group" v-if="formulaire.situation === 'AFFECTE'">
                    <label for="salle">Salle</label>
                    <select
                        id="salle"
                        v-model="formulaire.salle"
                    >
                        <option value="">-- Aucune salle --</option>
                        <option
                            v-for="salle in salles"
                            :key="salle.id"
                            :value="salle.id"
                        >
                            {{ salle.nom }}
                        </option>
                    </select>
                </div>

                <p v-if="erreur" class="error">{{ erreur }}</p>

                <div class="form-actions">
                    <button
                        type="button"
                        @click="$emit('close')"
                        :disabled="enCours"
                    >
                        Annuler
                    </button>
                    <button
                        type="submit"
                        :disabled="enCours"
                    >
                        {{ enCours ? 'Enregistrement...' : 'Enregistrer' }}
                    </button>
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { getSalles } from '../services/salleService';

const props = defineProps({
    mode: {
        type: String,
        default: 'creation'
    },
    equipement: {
        type: Object,
        default: null
    }
});

const emit = defineEmits(['close', 'save']);

const formulaire = ref({
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
});

const salles = ref([]);
const enCours = ref(false);
const erreur = ref('');

async function chargerSalles() {
    try {
        salles.value = await getSalles();
    } catch (error) {
        console.error('Erreur lors du chargement des salles:', error);
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

async function enregistrer() {
    enCours.value = true;
    erreur.value = '';

    try {
        emit('save', { ...formulaire.value });
    } catch (error) {
        erreur.value = error.message || 'Une erreur est survenue';
    } finally {
        enCours.value = false;
    }
}

watch(() => props.equipement, (nouvelEquipement) => {
    if (nouvelEquipement) {
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
    } else {
        formulaire.value = {
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
}, { immediate: true });

onMounted(() => {
    chargerSalles();
});
</script>

<style scoped>
.modal-overlay {
    position: fixed;
    inset: 0;
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
    background: rgba(0, 0, 0, 0.45);
}

.modal {
    width: 600px;
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    padding: 25px;
    background: white;
    border-radius: 10px;
}

.modal h2 {
    margin-top: 0;
    margin-bottom: 20px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 600;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 6px;
    box-sizing: border-box;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.form-actions button {
    padding: 10px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.form-actions button:last-child {
    background: #2563eb;
    color: white;
}

.form-actions button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.error {
    color: #b00020;
    margin-top: 10px;
}
</style>
