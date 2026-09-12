<template>
    <div class="page">

        <div class="page-header">
            <div>
                <h1>Équipements de la salle</h1>

                <p v-if="salle">
                    Salle : {{ salle.nom }}
                </p>
            </div>
        </div>


        <!-- Chargement -->
        <p v-if="loading">
            Chargement des équipements...
        </p>


        <!-- Erreur -->
        <p v-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>


        <!-- Liste des équipements -->
        <div
            v-if="!loading && equipements.length > 0"
            class="equipements-list"
        >

            <div
                v-for="equipement in equipements"
                :key="equipement.id"
                class="equipement-card"
            >

                <div class="equipement-info">

                    <h2>
                        {{ equipement.nom }}
                    </h2>

                    <p>
                        <strong>N° inventaire :</strong>
                        {{ equipement.numero_inventaire }}
                    </p>

                    <p>
                        <strong>Type :</strong>
                        {{ equipement.type }}
                    </p>

                    <p>
                        <strong>Fabricant :</strong>
                        {{ equipement.fabricant || "Non renseigné" }}
                    </p>

                    <p>
                        <strong>Modèle :</strong>
                        {{ equipement.modele || "Non renseigné" }}
                    </p>

                    <p>
                        <strong>N° série :</strong>
                        {{ equipement.numero_serie || "Non renseigné" }}
                    </p>

                    <p>
                        <strong>Adresse IP :</strong>
                        {{ equipement.adresse_ip || "Non renseignée" }}
                    </p>

                </div>


                <button
                    class="btn-view"
                    @click="voirEquipement(equipement.id)"
                >
                    Voir le détail
                </button>

            </div>

        </div>


        <!-- Aucun équipement -->
        <p
            v-if="!loading && equipements.length === 0"
            class="empty"
        >
            Aucun équipement enregistré dans cette salle.
        </p>

    </div>
</template>


<script setup>

import {
    ref,
    onMounted,
} from "vue";

import {
    useRoute,
    useRouter,
} from "vue-router";

import {
    getSalle,
} from "../services/salleService";

import {
    getEquipementsParSalle,
} from "../services/equipementService";


const route = useRoute();
const router = useRouter();


// Données
const salle = ref(null);
const equipements = ref([]);

const loading = ref(false);
const errorMessage = ref("");


// Charger la salle et ses équipements
async function chargerDonnees() {

    loading.value = true;
    errorMessage.value = "";

    try {

        const salleId = route.params.salleId;

        // Récupérer les informations de la salle
        salle.value = await getSalle(salleId);

        // Récupérer les équipements de cette salle
        equipements.value =
            await getEquipementsParSalle(salleId);

    } catch (error) {

        console.error(error);

        errorMessage.value =
            "Impossible de charger les équipements.";

    } finally {

        loading.value = false;

    }
}


// Aller vers le détail de l'équipement
function voirEquipement(id) {

    router.push(
        `/equipements/${id}`
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
    margin-bottom: 30px;
}


.page-header h1 {
    margin-bottom: 5px;
}


.page-header p {
    margin: 0;
    color: #666;
}


.equipements-list {
    display: grid;

    grid-template-columns:
        repeat(
            auto-fill,
            minmax(300px, 1fr)
        );

    gap: 20px;
}


.equipement-card {
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    border: 1px solid #ddd;
    border-radius: 10px;

    padding: 20px;

    background: white;
}


.equipement-card h2 {
    margin-top: 0;
}


.equipement-card p {
    margin: 8px 0;
}


.btn-view {
    margin-top: 20px;

    padding: 10px 14px;

    border: none;
    border-radius: 6px;

    cursor: pointer;

    background: #222;
    color: white;
}


.error {
    color: #b00020;
}


.empty {
    color: #666;
}

</style>