<template>
    <header class="app-header">
        <div class="app-header__inner">

            <router-link
                to="/dashboard-public"
                class="app-header__brand"
            >
                <span class="app-header__logo" aria-hidden="true">GPI</span>

                <span class="app-header__titles">
                    <span class="app-header__title">
                        Gestion du Parc Informatique
                    </span>

                    <span class="app-header__subtitle">
                        Consultation publique
                    </span>
                </span>
            </router-link>

            <button
                type="button"
                class="app-header__toggle"
                :aria-expanded="menuOuvert ? 'true' : 'false'"
                aria-controls="navigation-publique"
                @click="menuOuvert = !menuOuvert"
            >
                <span class="visually-hidden">
                    Ouvrir ou fermer la navigation
                </span>

                <svg
                    viewBox="0 0 24 24"
                    width="22"
                    height="22"
                    aria-hidden="true"
                    focusable="false"
                >
                    <path
                        :d="menuOuvert ? 'M6 6l12 12M18 6L6 18' : 'M4 7h16M4 12h16M4 17h16'"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                    />
                </svg>
            </button>

            <nav
                id="navigation-publique"
                class="app-header__nav"
                :class="{ 'app-header__nav--open': menuOuvert }"
                aria-label="Navigation principale"
            >
                <ul>
                    <li
                        v-for="lien in liensPublics"
                        :key="lien.to"
                    >
                        <router-link
                            :to="lien.to"
                            @click="menuOuvert = false"
                        >
                            {{ lien.label }}
                        </router-link>
                    </li>
                </ul>

                <router-link
                    to="/login"
                    class="btn-primary btn-sm"
                    @click="menuOuvert = false"
                >
                    Espace administrateur
                </router-link>
            </nav>

        </div>
    </header>
</template>

<script setup>
/**
 * En-tête de l'espace public (mode visiteur).
 *
 * La navigation n'expose que des fonctions réellement accessibles
 * sans authentification. L'accès administrateur passe par /login.
 */
import { ref } from "vue";

const menuOuvert = ref(false);

/*
 * Routes publiques réellement déclarées dans router/index.js.
 * Aucune entrée n'est ajoutée pour une fonctionnalité inexistante.
 */
const liensPublics = [
    { to: "/dashboard-public", label: "Accueil" },
    { to: "/equipements", label: "Équipements" },
    { to: "/plan", label: "Plans" },
    { to: "/signaler", label: "Signaler un problème" },
];
</script>

<style scoped>
.app-header {
    position: sticky;
    top: 0;
    z-index: 200;
    background-color: var(--bg-surface);
    border-bottom: 1px solid var(--border-light);
}

.app-header__inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    max-width: 1280px;
    min-height: var(--navbar-height);
    margin: 0 auto;
    padding: 0 1.25rem;
}

/* --- Marque --- */

.app-header__brand {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: inherit;
}

.app-header__logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: var(--radius-md);
    background-color: var(--primary);
    color: var(--on-primary);
    font-size: 0.8125rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.app-header__titles {
    display: flex;
    flex-direction: column;
    line-height: 1.25;
}

.app-header__title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-main);
}

.app-header__subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
}

/* --- Navigation --- */

.app-header__nav {
    display: flex;
    align-items: center;
    gap: 1.25rem;
}

.app-header__nav ul {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    list-style: none;
    margin: 0;
    padding: 0;
}

.app-header__nav a:not(.btn-primary) {
    display: block;
    padding: 0.45rem 0.7rem;
    border-radius: var(--radius-md);
    color: var(--secondary);
    font-size: 0.9rem;
    font-weight: 500;
}

.app-header__nav a:not(.btn-primary):hover {
    background-color: var(--bg-subtle);
    color: var(--text-main);
}

.app-header__nav a.router-link-exact-active:not(.btn-primary) {
    background-color: var(--primary-light);
    color: var(--primary);
    font-weight: 600;
}

/* --- Bascule mobile --- */

.app-header__toggle {
    display: none;
    padding: 0.4rem;
    background-color: transparent;
    color: var(--text-main);
    border: 1px solid var(--border-medium);
}

.app-header__toggle:hover {
    background-color: var(--bg-subtle);
}

/* --- Small screens --- */

@media (max-width: 860px) {
    .app-header__toggle {
        display: inline-flex;
    }

    .app-header__nav {
        display: none;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        flex-direction: column;
        align-items: stretch;
        gap: 0.75rem;
        padding: 1rem 1.25rem 1.25rem;
        background-color: var(--bg-surface);
        border-bottom: 1px solid var(--border-light);
        box-shadow: var(--shadow-md);
    }

    .app-header__nav--open {
        display: flex;
    }

    .app-header__nav ul {
        flex-direction: column;
        align-items: stretch;
        gap: 0.15rem;
    }

    .app-header__nav a:not(.btn-primary) {
        padding: 0.65rem 0.75rem;
    }
}
</style>
