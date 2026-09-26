<template>
    <div class="dashboard-public">
        <header class="dashboard-header">
            <div class="header-content">
                <h1>GPI - Système de Gestion du Parc Informatique</h1>
                <p>Interface visiteur</p>
            </div>
            <button class="login-button" @click="allerVersLogin">
                Connexion Administrateur
            </button>
        </header>

        <div class="dashboard-content">
            <div class="welcome-section">
                <h2>Bienvenue sur le système GPI</h2>
                <p>Consultez les équipements, le plan graphique et signalez des problèmes.</p>
            </div>

            <div class="cards-grid">
                <div class="dashboard-card" @click="allerVersSignalement">
                    <div class="card-icon">🎫</div>
                    <h3>Signaler un problème</h3>
                    <p>Créez un ticket de panne pour un équipement</p>
                </div>

                <div class="dashboard-card" @click="allerVersPlan">
                    <div class="card-icon">🗺️</div>
                    <h3>Plan graphique</h3>
                    <p>Visualisez la localisation des équipements</p>
                </div>

                <div class="dashboard-card" @click="allerVersEquipements">
                    <div class="card-icon">💻</div>
                    <h3>Équipements</h3>
                    <p>Consultez la liste du parc informatique</p>
                </div>
            </div>

            <div class="info-section">
                <h3>Informations</h3>
                <ul>
                    <li>En tant que visiteur, vous pouvez consulter les équipements et le plan en lecture seule</li>
                    <li>Vous pouvez signaler des problèmes via le formulaire de tickets</li>
                    <li>Pour gérer le parc informatique, connectez-vous en tant qu'administrateur</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

function allerVersLogin() {
    router.push('/login');
}

function allerVersSignalement() {
    router.push('/signaler');
}

function allerVersPlan() {
    router.push('/plan');
}

function allerVersEquipements() {
    router.push('/equipements');
}
</script>

<style scoped>
.dashboard-public {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.dashboard-header {
    background: rgba(255, 255, 255, 0.95);
    padding: 20px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
    margin: 0;
    font-size: 24px;
    color: #333;
}

.header-content p {
    margin: 5px 0 0;
    color: #666;
    font-size: 14px;
}

.login-button {
    padding: 12px 24px;
    background: #333;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.3s;
}

.login-button:hover {
    background: #555;
}

.dashboard-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
}

.welcome-section {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 12px;
    margin-bottom: 30px;
    text-align: center;
}

.welcome-section h2 {
    margin: 0 0 10px;
    color: #333;
}

.welcome-section p {
    margin: 0;
    color: #666;
}

.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.dashboard-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 12px;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
    text-align: center;
}

.dashboard-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.card-icon {
    font-size: 48px;
    margin-bottom: 15px;
}

.dashboard-card h3 {
    margin: 0 0 10px;
    color: #333;
}

.dashboard-card p {
    margin: 0;
    color: #666;
    font-size: 14px;
}

.info-section {
    background: rgba(255, 255, 255, 0.95);
    padding: 30px;
    border-radius: 12px;
}

.info-section h3 {
    margin: 0 0 15px;
    color: #333;
}

.info-section ul {
    margin: 0;
    padding-left: 20px;
    color: #666;
}

.info-section li {
    margin-bottom: 10px;
}
</style>
