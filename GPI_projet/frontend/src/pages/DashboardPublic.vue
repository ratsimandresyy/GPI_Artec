<template>
    <div class="page-container accueil-public">

        <section class="accueil-hero">
            <h1>
                Gestion et localisation des actifs informatiques
            </h1>

            <p class="accueil-hero__lead">
                GPIcentralise l'inventaire du parc informatique et sa
                localisation dans les bâtiments. En tant que visiteur, vous
                pouvez consulter ces informations et signaler un problème.
            </p>
        </section>

        <section
            class="accueil-section"
            aria-labelledby="titre-fonctions"
        >
            <h2
                id="titre-fonctions"
                class="accueil-section__titre"
            >
                Accès rapides
            </h2>

            <ul class="accueil-grille">
                <li
                    v-for="entree in entrees"
                    :key="entree.to"
                >
                    <router-link
                        :to="entree.to"
                        class="accueil-carte"
                    >
                        <span
                            class="accueil-carte__icone"
                            aria-hidden="true"
                            v-html="entree.icone"
                        />

                        <span class="accueil-carte__corps">
                            <span class="accueil-carte__titre">
                                {{ entree.titre }}
                            </span>

                            <span class="accueil-carte__texte">
                                {{ entree.texte }}
                            </span>
                        </span>
                    </router-link>
                </li>
            </ul>
        </section>

        <section
            class="accueil-section"
            aria-labelledby="titre-informations"
        >
            <h2
                id="titre-informations"
                class="accueil-section__titre"
            >
                Mode visiteur
            </h2>

            <div class="accueil-informations">
                <ul>
                    <li>
                        Consultation des équipements, de leur
                        localisation, des bâtiments, des étages et des
                        plans, en lecture seule.
                    </li>
                    <li>
                        Création d'un signalement pour une panne ou une
                        réclamation.
                    </li>
                    <li>
                        Aucune modification du parc : l'administration,
                        la gestion du stock et le traitement des
                        signalements sont réservés à l'administrateur.
                    </li>
                </ul>

                <p class="accueil-informations__action">
                    <router-link
                        to="/login"
                        class="btn-primary"
                    >
                        Connexion administrateur
                    </router-link>
                </p>
            </div>
        </section>

    </div>
</template>

<script setup>
/**
 * Accueil public (mode visiteur).
 *
 * Les données proviennent exclusivement des fonctionnalités
 * réellement exposées par l'API publique. Aucune statistique n'est
 * calculée ni inventée ici.
 */
const entrees = [
    {
        to: "/equipements",
        titre: "Équipements",
        texte:
            "Consultez les matériels du parc et leur numéro d'inventaire.",
        icone:
            '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" ' +
            'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" ' +
            'stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" ' +
            'rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
    },
    {
        to: "/plan",
        titre: "Plans et localisation",
        texte:
            "Visualisez la position des équipements sur le plan de chaque étage.",
        icone:
            '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" ' +
            'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" ' +
            'stroke-linejoin="round"><path d="M3 6l6-3 6 3 6-3v15l-6 3-6-3-6 3z"/>' +
            '<path d="M9 3v15M15 6v15"/></svg>',
    },
    {
        to: "/signaler",
        titre: "Signaler un problème",
        texte:
            "Déclarez une panne ou une réclamation sur un équipement.",
        icone:
            '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" ' +
            'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" ' +
            'stroke-linejoin="round"><path d="M12 9v4M12 17h.01"/>' +
            '<path d="M10.3 3.9L2.4 18a2 2 0 001.7 3h15.8a2 2 0 001.7-3L13.7 3.9a2 2 0 00-3.4 0z"/></svg>',
    },
];
</script>

<style scoped>
.accueil-public {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

/* --- Bandeau --- */

.accueil-hero {
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--border-light);
}

.accueil-hero h1 {
    max-width: 22ch;
    margin-bottom: 0.6rem;
    font-size: 1.85rem;
    line-height: 1.2;
}

.accueil-hero__lead {
    max-width: 62ch;
    margin: 0;
    font-size: 1.05rem;
}

/* --- Sections --- */

.accueil-section {
    margin-top: 0;
}

.accueil-section__title {
    margin-bottom: 1rem;
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    text-transform: uppercase;
    color: var(--text-muted);
}

/* --- Grille de cartes --- */

.accueil-grille {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1rem;
    list-style: none;
    margin: 0;
    padding: 0;
}

.accueil-carte {
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    height: 100%;
    padding: 1.1rem 1.15rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    color: inherit;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.accueil-carte:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow-md);
    color: inherit;
}

.accueil-carte__icone {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    width: 2.35rem;
    height: 2.35rem;
    border-radius: var(--radius-md);
    background-color: var(--primary-light);
    color: var(--primary);
}

.accueil-carte__corps {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.accueil-carte__titre {
    font-weight: 600;
    color: var(--text-main);
}

.accueil-carte__texte {
    font-size: 0.9rem;
    color: var(--text-muted);
}

/* --- Informations --- */

.accueil-informations {
    padding: 1.25rem 1.35rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
}

.accueil-informations ul {
    margin: 0 0 1.1rem;
    padding-left: 1.15rem;
    color: var(--text-muted);
}

.accueil-informations li {
    margin-bottom: 0.5rem;
}

.accueil-informations p {
    margin: 0;
}

.accueil-informations__action {
    margin: 1.1rem 0 0;
}

.accueil-informations p {
    margin: 0;
}

@media (max-width: 640px) {
    .accueil-public {
        padding: 0;
    }

    .accueil-hero h1 {
        font-size: 1.5rem;
    }

    .accueil-hero__lead {
        font-size: 1rem;
    }
}
</style>
