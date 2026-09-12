<template>
    <div class="equipement-detail">

        <button @click="retour">
            ← Retour aux équipements
        </button>

        <h1>Détail de l'équipement</h1>

        <!-- Chargement -->
        <p v-if="loading">
            Chargement...
        </p>

        <!-- Erreur -->
        <p v-else-if="errorMessage" class="error">
            {{ errorMessage }}
        </p>

        <!-- Informations -->
        <div v-else-if="equipement" class="card">

            <h2>{{ equipement.nom }}</h2>

            <div class="information">
                <strong>ID :</strong>
                <span>{{ equipement.id }}</span>
            </div>

            <div class="information">
                <strong>Type :</strong>
                <span>{{ equipement.type }}</span>
            </div>

            <div class="information">
                <strong>Numéro d'inventaire :</strong>
                <span>
                    {{ equipement.numero_inventaire }}
                </span>
            </div>

            <div class="information">
                <strong>Numéro de série :</strong>
                <span>
                    {{ equipement.numero_serie || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Fabricant :</strong>
                <span>
                    {{ equipement.fabricant || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Modèle :</strong>
                <span>
                    {{ equipement.modele || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Adresse IP :</strong>
                <span>
                    {{ equipement.adresse_ip || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Adresse MAC :</strong>
                <span>
                    {{ equipement.adresse_mac || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Salle :</strong>
                <span>
                    {{ equipement.salle || "-" }}
                </span>
            </div>

            <div class="information">
                <strong>Actif :</strong>
                <span>
                    {{ equipement.actif ? "Oui" : "Non" }}
                </span>
            </div>

        </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getEquipement } from "../services/equipementService";

const route = useRoute();
const router = useRouter();

const equipement = ref(null);
const loading = ref(false);
const errorMessage = ref("");

/**
 * Récupère l'identifiant présent dans l'URL.
 */
const id = route.params.id;

/**
 * Charge l'équipement depuis l'API.
 */
async function chargerEquipement() {
    loading.value = true;
    errorMessage.value = "";

    try {
        equipement.value = await getEquipement(id);

    } catch (error) {

        console.error(
            "Erreur lors du chargement de l'équipement :",
            error
        );

        errorMessage.value =
            "Impossible de charger cet équipement.";

    } finally {
        loading.value = false;
    }
}

/**
 * Retourne à la liste des équipements.
 */
function retour() {
    router.push("/equipements");
}

onMounted(() => {
    chargerEquipement();
});
</script>

<style scoped>

.equipement-detail {
    padding: 30px;
}

.card {
    max-width: 700px;
    margin-top: 20px;
    padding: 25px;
    border: 1px solid #ddd;
    border-radius: 10px;
}

.information {
    display: flex;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid #eee;
}

.error {
    color: red;
}

button {
    padding: 8px 15px;
    cursor: pointer;
}

</style>