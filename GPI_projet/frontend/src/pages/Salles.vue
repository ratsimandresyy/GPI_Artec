<template>
    <div class="page">

        <div class="page-header">
            <div>
                <h1>Salles</h1>

                <p v-if="etage">
                    Étage : {{ etage.nom }}
                </p>
            </div>

            <button
                v-if="estAdmin"
                class="btn-primary"
                @click="ouvrirFormulaire"
            >
                + Ajouter une salle
            </button>
        </div>


        <p v-if="loading">
            Chargement des salles...
        </p>


        <p v-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>


        <!-- Liste des salles -->
        <div
            v-if="!loading && salles.length > 0"
            class="salles-grid"
        >

            <div
                v-for="salle in salles"
                :key="salle.id"
                class="salle-card"
            >

                <h2>
                    {{ salle.nom }}
                </h2>

                <p>
                    {{ salle.description || "Aucune description" }}
                </p>


                <div class="actions">

                    <button
                        class="btn-view"
                        @click="voirSalle(salle.id)"
                    >
                        Voir
                    </button>

                    <template v-if="estAdmin">

                        <button
                            class="btn-edit"
                            @click="modifier(salle)"
                        >
                            Modifier
                        </button>

                        <button
                            class="btn-delete"
                            @click="supprimer(salle)"
                        >
                            Supprimer
                        </button>

                    </template>

                </div>

            </div>

        </div>


        <p
            v-if="!loading && salles.length === 0"
            class="empty"
        >
            Aucune salle enregistrée pour cet étage.
        </p>


        <!-- Formulaire -->
        <div
            v-if="formulaireVisible"
            class="form-container"
        >

            <h2>
                {{ modeEdition
                    ? "Modifier la salle"
                    : "Ajouter une salle"
                }}
            </h2>


            <form @submit.prevent="enregistrer">

                <div class="form-group">

                    <label for="nom">
                        Nom
                    </label>

                    <input
                        id="nom"
                        v-model="formulaire.nom"
                        type="text"
                        required
                    >

                </div>


                <div class="form-group">

                    <label for="description">
                        Description
                    </label>

                    <textarea
                        id="description"
                        v-model="formulaire.description"
                        rows="4"
                    ></textarea>

                </div>


                <div class="form-actions">

                    <button
                        type="submit"
                        class="btn-primary"
                    >
                        Enregistrer
                    </button>

                    <button
                        type="button"
                        class="btn-secondary"
                        @click="fermerFormulaire"
                    >
                        Annuler
                    </button>

                </div>

            </form>

        </div>

    </div>
</template>


<script setup>

import {
    ref,
    computed,
    onMounted,
} from "vue";

import {
    useRoute,
    useRouter,
} from "vue-router";

import {
    getSalles,
    creerSalle,
    modifierSalle,
    supprimerSalle,
} from "../services/salleService";

import {
    getEtage,
} from "../services/etageService";

import {
    useAuthStore,
} from "../stores/auth";


const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();


// Données
const salles = ref([]);
const etage = ref(null);

const loading = ref(false);
const errorMessage = ref("");


// Formulaire
const formulaireVisible = ref(false);
const modeEdition = ref(false);

const salleEnCours = ref(null);

const formulaire = ref({
    nom: "",
    description: "",
});


// Vérification du rôle
const estAdmin = computed(() => {
    return authStore.isAdmin;
});


// Charger les données
async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const etageId = route.params.etageId;

        // Récupérer l'étage courant
        etage.value = await getEtage(etageId);

        // Récupérer toutes les salles
        const toutesLesSalles = await getSalles();

        // Garder uniquement les salles
        // appartenant à l'étage sélectionné.
        salles.value = toutesLesSalles.filter(
            (salle) =>
                String(salle.etage) === String(etageId)
        );

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les salles.";

    } finally {

        loading.value = false;

    }
}


// Ouvrir le formulaire
function ouvrirFormulaire() {

    modeEdition.value = false;

    salleEnCours.value = null;

    formulaire.value = {
        nom: "",
        description: "",
    };

    formulaireVisible.value = true;
}


// Modifier
function modifier(salle) {

    modeEdition.value = true;

    salleEnCours.value = salle;

    formulaire.value = {
        nom: salle.nom,
        description: salle.description || "",
    };

    formulaireVisible.value = true;
}


// Fermer le formulaire
function fermerFormulaire() {
    formulaireVisible.value = false;
}


// Enregistrer
async function enregistrer() {

    try {

        const donnees = {
            etage: route.params.etageId,
            nom: formulaire.value.nom,
            description: formulaire.value.description,
        };


        if (modeEdition.value) {

            await modifierSalle(
                salleEnCours.value.id,
                donnees
            );

        } else {

            await creerSalle(donnees);

        }


        fermerFormulaire();

        await chargerDonnees();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible d'enregistrer la salle.";

    }
}


// Supprimer
async function supprimer(salle) {

    const confirmation = confirm(
        `Voulez-vous supprimer la salle "${salle.nom}" ?`
    );

    if (!confirmation) {
        return;
    }


    try {

        await supprimerSalle(salle.id);

        await chargerDonnees();

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de supprimer la salle.";

    }
}


// Voir une salle
function voirSalle(id) {

    console.log(
        "Salle sélectionnée :",
        id
    );

    router.push(
        `/salles/${id}/equipements`
    );

}

onMounted(() => {
    chargerDonnees();
});

</script>


<style scoped>

.page {
    width: 100%;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.page-header h1 {
    margin-bottom: 5px;
}

.page-header p {
    margin: 0;
    color: #666;
}


.salles-grid {
    display: grid;
    grid-template-columns: repeat(
        auto-fill,
        minmax(250px, 1fr)
    );
    gap: 20px;
}


.salle-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 20px;
    background: white;
}


.salle-card h2 {
    margin-top: 0;
}


.actions {
    display: flex;
    gap: 8px;
    margin-top: 20px;
    flex-wrap: wrap;
}


button {
    border: none;
    border-radius: 6px;
    padding: 9px 14px;
    cursor: pointer;
}


.btn-primary {
    background: #222;
    color: white;
}


.btn-view {
    background: #eee;
}


.btn-edit {
    background: #ddd;
}


.btn-delete {
    background: #f5d5d5;
}


.btn-secondary {
    background: #eee;
}


.form-container {
    margin-top: 30px;
    padding: 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
    max-width: 500px;
}


.form-group {
    margin-bottom: 15px;
}


.form-group label {
    display: block;
    margin-bottom: 5px;
}


.form-group input,
.form-group textarea {
    width: 100%;
    box-sizing: border-box;
    padding: 10px;
}


.form-actions {
    display: flex;
    gap: 10px;
}


.error {
    color: #b00020;
}


.empty {
    color: #666;
}

</style>