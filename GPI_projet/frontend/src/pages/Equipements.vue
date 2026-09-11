<template>
    <div class = "equipements-page">
        <h1>Equipements</h1>

        <!--Chargement-->
        <p v-if="loading">
            Chargement des equipements...
        </p>

        <!--Erreur-->
        <p v-else-if="errorMessage" class="error">
            {{  errorMessage }}
        </p>

        <!-- Tableau -->
         <table v-else>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nom</th>
                    <th>N inventaire</th>
                    <th>Fabricant</th>
                    <th>Modele</th>
                    <th>Adresse IP</th>
                    <th>Actif</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="equipement in equipements":key="equipement.id">
                    <td>{{ equipement.id }}</td>
                    <td>{{ equipement.nom }}</td>
                    <td>{{ equipement.numero_inventaire }}</td>
                    <td>{{ equipement.fabricant }}</td>
                    <td>{{ equipement.modele }}</td>
                    <td>{{ equipement.adresse_ip || "-" }}</td>
                    <td>{{ equipement.actif ? "Oui" : "Non" }}</td>
                </tr>
            </tbody>
         </table>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getEquipements } from '../services/equipementService';

const equipements = ref([]);
const loading = ref(false);
const errorMessage = ref("");

async function chargerEquipements() {
    loading.value = true;
    errorMessage.value = "";

    try {
        equipements.value = await getEquipements();
    } catch (error) {
        console.error(
            "Erreur lors du chargement des equipements :", error
        );

        errorMessage.value =
            "Impossible de charger les equipements.";
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    chargerEquipements();
});
</script>

<style scoped>
    .equipements-page {
        padding: 30px;
    }

    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }

    th,
    td {
        border: 1px solid #ddd;
        padding: 10px;
        text-align: left;
    }

    th {
    font-weight: bold;
    }

    .error {
        color: red;
    }
</style>
