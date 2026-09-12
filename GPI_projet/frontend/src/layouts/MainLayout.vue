<template>
    <div class="app-layout">

        <!-- Barre supérieure -->
        <header class="navbar">
            <div class="navbar-brand">GPI</div>

            <div class="navbar-user">Système de gestion du parc informatique</div>
        </header>

        <!-- Corps de l'application -->
        <div class="app-body">

            <!-- Menu latéral -->
            <aside class="sidebar">

                <nav>
                    <ul>

                        <li>
                            <router-link to="/dashboard">Dashboard</router-link>
                        </li>

                        <li>
                            <router-link to="/equipements">Équipements</router-link>
                        </li>

                        <li>
                            <router-link to="/batiments">Bâtiments</router-link>
                        </li>

                        <li>
                            <router-link to="/localisation">Localisation</router-link>
                        </li>

                        <li>
                            <router-link to="/audits">Audits</router-link>
                        </li>

                    </ul>
                </nav>


                <!-- Déconnexion -->
                <div class="sidebar-bottom">

                    <button type="button" @click="seDeconnecter">Déconnexion</button>
                </div>

            </aside>

            <!-- Contenu de la page -->
            <main class="main-content">

                <router-view />

            </main>

        </div>

    </div>
</template>


<script setup>

import { useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";


const router = useRouter();

const authStore = useAuthStore();


function seDeconnecter() {

    console.log("Bouton déconnexion cliqué");

    authStore.seDeconnecter();

    console.log(
        "Token après déconnexion :",
        localStorage.getItem("accessToken")
    );

    router.push("/login");

}

</script>


<style scoped>

.app-layout {
    min-height: 100vh;
}


/* =========================
   NAVBAR
   ========================= */

.navbar {
    height: 60px;

    display: flex;
    align-items: center;
    justify-content: space-between;

    padding: 0 25px;

    border-bottom: 1px solid #ddd;
}


.navbar-brand {
    font-size: 24px;
    font-weight: bold;
}


.navbar-user {
    font-size: 14px;
}


/* =========================
   CORPS
   ========================= */

.app-body {
    display: flex;

    min-height: calc(100vh - 60px);
}


/* =========================
   SIDEBAR
   ========================= */

.sidebar {
    width: 220px;

    padding: 20px;

    border-right: 1px solid #ddd;

    display: flex;
    flex-direction: column;
    justify-content: space-between;
}


.sidebar ul {
    list-style: none;

    padding: 0;
    margin: 0;
}


.sidebar li {
    margin-bottom: 8px;
}


.sidebar a {
    display: block;

    padding: 10px;

    text-decoration: none;
}


.sidebar a.router-link-active {
    font-weight: bold;
}


/* =========================
   DECONNEXION
   ========================= */

.sidebar-bottom button {
    width: 100%;

    padding: 10px;

    cursor: pointer;
}


/* =========================
   CONTENU
   ========================= */

.main-content {
    flex: 1;

    padding: 30px;
}

</style>