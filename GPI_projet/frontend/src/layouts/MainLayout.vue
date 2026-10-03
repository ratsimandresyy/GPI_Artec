<template>
    <div class="app-layout">

        <!-- Barre supérieure -->

        <header class="topbar">

            <button
                type="button"
                class="topbar__toggle"
                :aria-expanded="menuOuvert ? 'true' : 'false'"
                aria-controls="navigation-administration"
                @click="menuOuvert = !menuOuvert"
            >
                <span class="visually-hidden">
                    Ouvrir ou fermer le menu
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

            <router-link
                to="/dashboard"
                class="topbar__brand"
            >
                <span class="topbar__logo" aria-hidden="true">GPI</span>

                <span class="topbar__title">
                    Gestion du Parc Informatique
                </span>
            </router-link>

            <div
                v-if="utilisateur"
                class="topbar__user"
            >
                <span
                    class="user-avatar"
                    aria-hidden="true"
                >
                    {{ initiales }}
                </span>

                <span class="user-details">
                    <span class="user-name">
                        {{ utilisateur.username }}
                    </span>

                    <span class="role-badge">
                        Administrateur
                    </span>
                </span>

                <button
                    type="button"
                    class="btn-ghost btn-sm"
                    @click="seDeconnecter"
                >
                    Déconnexion
                </button>
            </div>

        </header>

        <div class="app-body">

            <!-- Voile mobile -->

            <div
                v-if="menuOuvert"
                class="sidebar-backdrop"
                @click="menuOuvert = false"
            ></div>

            <!-- Menu latéral -->

            <aside
                id="navigation-administration"
                class="sidebar"
                :class="{ 'sidebar--open': menuOuvert }"
            >

                <nav
                    class="sidebar__nav"
                    aria-label="Navigation d'administration"
                >
                    <p class="sidebar__section">
                        Parc
                    </p>

                    <ul>
                        <li
                            v-for="lien in liensParc"
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

                    <p class="sidebar__section">
                        Exploitation
                    </p>

                    <ul>
                        <li
                            v-for="lien in liensExploitation"
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

                    <p class="sidebar__section">
                        Administration
                    </p>

                    <ul>
                        <li
                            v-for="lien in liensAdministration"
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
                </nav>

                <div class="sidebar__bottom">
                    <router-link
                        to="/profile"
                        class="sidebar__link"
                        @click="menuOuvert = false"
                    >
                        Mon profil
                    </router-link>
                </div>

            </aside>

            <!-- Contenu de la page -->

            <main
                id="contenu-principal"
                class="main-content"
            >
                <router-view />
            </main>

        </div>

        <NotificationToast />

    </div>
</template>

<script setup>
/**
 * Shell de l'espace d'administration.
 *
 * La liste des entrées de menu est déclarée ici, en un seul endroit,
 * à partir des routes réellement existantes. L'état d'authentification
 * et le rôle proviennent exclusivement du store Pinia.
 */
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { useAuthStore } from "../stores/auth";

import NotificationToast from "../components/NotificationToast.vue";

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const menuOuvert = ref(false);

/*
 * L'accès à ce layout est déjà réservé à l'administrateur par le
 * routeur ; `estAdmin` sert à afficher l'identité de session.
 */
const utilisateur = computed(() => authStore.user);

const initiales = computed(() => {
    const nom = utilisateur.value?.username || "?";

    return nom.slice(0, 2).toUpperCase();
});

/*
 * Groupes de navigation. Chaque entrée correspond à une route
 * déclarée dans router/index.js.
 */
const liensParc = [
    { to: "/dashboard", label: "Tableau de bord" },
    { to: "/equipements", label: "Équipements" },
    { to: "/batiments", label: "Bâtiments" },
    { to: "/localisation", label: "Localisation" },
];

const liensExploitation = [
    { to: "/stock", label: "Stock et maintenance" },
    { to: "/tickets", label: "Signalements" },
    { to: "/audits", label: "Audits WinAudit" },
];

const liensAdministration = [
    { to: "/utilisateurs", label: "Utilisateurs" },
];

// Referme le menu mobile dès que la page change.
watch(
    () => route.fullPath,
    () => {
        menuOuvert.value = false;
    },
);

function seDeconnecter() {
    authStore.seDeconnecter();
    router.push("/dashboard-public");
}

/*
 * Échap referme le menu mobile, comme le fait déjà le voile au clic.
 *
 * L'écoute est portée par `document`, comme dans `Tickets.vue`,
 * `Utilisateurs.vue` et `ConfirmDialog.vue` : le focus peut être sur
 * le bouton hamburger, dans la navigation ou ailleurs, et le voile
 * n'est pas focusable.
 *
 * Le garde-fou sur `menuOuvert` évite de consommer l'Échap destiné à
 * une autre fermeture.
 */
function surTouche(event) {
    if (event.key === "Escape" && menuOuvert.value) {
        menuOuvert.value = false;
    }
}

onMounted(() => {
    document.addEventListener("keydown", surTouche);
});

onBeforeUnmount(() => {
    document.removeEventListener("keydown", surTouche);
});
</script>

<style scoped>
.app-layout {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

/* ==========================================================================
   Barre supérieure
   ========================================================================== */

.topbar {
    position: sticky;
    top: 0;
    z-index: 200;
    display: flex;
    align-items: center;
    gap: 1rem;
    min-height: var(--navbar-height);
    padding: 0 1.25rem;
    background-color: var(--bg-surface);
    border-bottom: 1px solid var(--border-light);
}

.topbar__toggle {
    display: none;
    padding: 0.4rem;
    background-color: transparent;
    color: var(--text-main);
    border: 1px solid var(--border-medium);
}

.topbar__toggle:hover {
    background-color: var(--bg-subtle);
}

.topbar__brand {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    color: inherit;
}

.topbar__logo {
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
}

.topbar__title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-main);
}

.topbar__user {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-left: auto;
}

.user-avatar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.1rem;
    height: 2.1rem;
    border-radius: 50%;
    background-color: var(--primary-light);
    color: var(--primary);
    font-size: 0.75rem;
    font-weight: 700;
}

.user-details {
    display: flex;
    flex-direction: column;
    line-height: 1.25;
}

.user-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--text-main);
}

.role-badge {
    display: inline-block;
    padding: 0.1rem 0.45rem;
    border-radius: var(--radius-full);
    background-color: var(--primary-light);
    color: var(--primary);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

/* ==========================================================================
   Corps
   ========================================================================== */

.app-body {
    display: flex;
    flex: 1;
    min-height: 0;
}

/* ==========================================================================
   Menu latéral
   ========================================================================== */

/*
    La sidebar porte le bleu institutionnel.

    Aucun aplat vert, aucune texture : le vert reste un accent
    réservé aux actions positives et aux indicateurs de succès.
*/
.sidebar {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    flex-shrink: 0;
    width: var(--sidebar-width);
    padding: 1.25rem 0.85rem;
    background-color: var(--primary-deep);
    border-right: 1px solid var(--primary-deep);
}

/*
    Texte de navigation : blanc à opacité réduite.
    Le blanc pur est réservé au titre d'application, à l'élément
    actif et au focus, pour que la hiérarchie reste lisible.
*/
.sidebar__section {
    margin: 1.1rem 0 0.4rem;
    padding: 0 0.6rem;
    color: rgba(255, 255, 255, 0.55);
    font-size: 0.6875rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.sidebar__section:first-child {
    margin-top: 0;
}

.sidebar__nav ul {
    list-style: none;
    margin: 0;
    padding: 0;
}

.sidebar__nav li {
    margin-bottom: 0.1rem;
}

.sidebar__nav a,
.sidebar__link {
    display: block;
    padding: 0.55rem 0.6rem;
    border-radius: var(--radius-md);
    color: rgba(255, 255, 255, 0.78);
    font-size: 0.9rem;
    font-weight: 500;
    transition: background-color 0.15s ease, color 0.15s ease;
}

.sidebar__nav a:hover,
.sidebar__link:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

/*
    Élément actif : fond blanc et texte bleu institutionnel.
    L'inversion de contraste porte l'information, la couleur seule
    ne la porte pas.
*/
.sidebar__nav a.router-link-active {
    background-color: #ffffff;
    color: var(--primary);
    font-weight: 600;
}

/* Le focus reste visible sur fond bleu. */
.sidebar__nav a:focus-visible,
.sidebar__link:focus-visible {
    outline: 2px solid #ffffff;
    outline-offset: 2px;
}

.sidebar__bottom {
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 0.6rem;
    margin-top: 1rem;
}

.sidebar-backdrop {
    display: none;
}

/* ==========================================================================
   Contenu
   ========================================================================== */

.main-content {
    flex: 1;
    min-width: 0;
    padding: 1.75rem 1.5rem;
}

/* ==========================================================================
   Tablette et mobile
   ========================================================================== */

@media (max-width: 1024px) {
    .main-content {
        padding: 1.5rem 1.25rem;
    }
}

@media (max-width: 860px) {
    .topbar__toggle {
        display: inline-flex;
    }

    .topbar__title {
        display: none;
    }

    .sidebar {
        position: fixed;
        top: var(--navbar-height);
        bottom: 0;
        left: 0;
        z-index: 300;
        width: 260px;
        transform: translateX(-100%);
        transition: transform 0.2s ease-in-out;
        box-shadow: var(--shadow-lg);
    }

    .sidebar--open {
        transform: translateX(0);
    }

    .sidebar-backdrop {
        display: block;
        position: fixed;
        top: var(--navbar-height);
        right: 0;
        bottom: 0;
        left: 0;
        z-index: 250;
        background-color: rgba(15, 23, 42, 0.45);
    }
}

@media (max-width: 640px) {
    .main-content {
        padding: 1.25rem 1rem;
    }

    .user-details {
        display: none;
    }
}
</style>
