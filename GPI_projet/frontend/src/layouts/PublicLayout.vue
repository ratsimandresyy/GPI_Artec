<template>
    <div class="public-layout">

        <AppHeader />

        <main
            id="contenu-principal"
            class="public-layout__main"
        >
            <router-view />
        </main>

        <NotificationToast />

        <footer class="public-layout__footer">
            <p>
                GPI — Gestion et localisation des actifs informatiques.
                Consultation publique en lecture seule.
            </p>

            <p class="text-muted">
                Les opérations d'administration sont réservées aux
                comptes authentifiés.
            </p>
        </footer>

    </div>
</template>

<script setup>
/**
 * Layout de l'espace public (mode visiteur).
 *
 * Il fournit l'en-tête, la zone de contenu et le pied de page.
 * Il ne protège rien : la sécurité réelle est assurée par le backend.
 */
import AppHeader from "../components/AppHeader.vue";
import NotificationToast from "../components/NotificationToast.vue";
</script>

<style scoped>
.public-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    background-color: var(--bg-page);
}

.public-layout__main {
    flex: 1;
    width: 100%;
    /*
     * Le layout porte la marge extérieure (gutter) ; les pages
     * appliquent `.page-container` pour la largeur maximale. Chaque
     * couche n'a donc qu'une seule responsabilité, ce qui évite le
     * cumul layout + page.
     */
    padding: 1.75rem 1.5rem;
}

.public-layout__footer {
    border-top: 1px solid var(--border-light);
    background-color: var(--bg-surface);
}

.public-layout__footer p {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0.4rem 1.25rem;
    font-size: 0.8125rem;
}

.public-layout__footer p:first-child {
    padding-top: 1.1rem;
    color: var(--text-main);
    font-weight: 500;
}

.public-layout__footer p:last-child {
    padding-bottom: 1.1rem;
}

@media (max-width: 1024px) {
    .public-layout__main {
        padding: 1.5rem 1.25rem;
    }
}

@media (max-width: 640px) {
    .public-layout__main {
        padding: 1.25rem 1rem;
    }

    .public-layout__footer p {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
