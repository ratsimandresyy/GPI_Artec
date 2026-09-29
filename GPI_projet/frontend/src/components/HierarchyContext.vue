<template>
    <nav
        v-if="etapes.length"
        class="hierarchie"
        aria-label="Fil de la hiérarchie du parc"
    >
        <ol class="hierarchie__liste">
            <li
                v-for="(etape, index) in etapes"
                :key="etape.cle"
                class="hierarchie__etape"
            >
                <!--
                    Le dernier niveau représente la page courante : il
                    est un texte, et non un lien.
                -->
                <router-link
                    v-if="etape.lien"
                    :to="etape.lien"
                    class="hierarchie__lien"
                >
                    {{ etape.libelle }}
                </router-link>

                <span
                    v-else
                    class="hierarchie__actuel"
                    aria-current="page"
                >
                    {{ etape.libelle }}
                </span>

                <span
                    v-if="index < etapes.length - 1"
                    class="hierarchie__separateur"
                    aria-hidden="true"
                >
                    /
                </span>
            </li>
        </ol>
    </nav>
</template>

<script setup>
/**
 * Contexte hiérarchique Bâtiment → Étage → Salle → Équipements.
 *
 * Chaque niveau est un lien vers la page correspondante, sauf le
 * dernier qui désigne la page courante. Cela donne à l'administrateur
 * le contexte permanent et un moyen naturel de remonter d'un cran,
 * sans ajouter de route ni de bouton « Retour » générique.
 *
 * Les entrées sont fournies par la page : ce composant ne connaît ni
 * les routes du parc, ni la façon dont elles sont chargées.
 */
import { computed } from "vue";

const props = defineProps({
    // Liste ordonnée du plus général au plus précis.
    // Chaque entrée : { cle, libelle, lien? }.
    niveaux: {
        type: Array,
        default: () => [],
    },
});

/*
 * Les niveaux sans libellé sont écartés : une hiérarchie à trous
 * (bâtiment encore en chargement) ne doit pas produire un séparateur
 * orphelin.
 */
const etapes = computed(() =>
    props.niveaux
        .filter((niveau) => niveau && niveau.libelle)
        .map((niveau) => ({
            cle: niveau.cle || niveau.libelle,
            libelle: niveau.libelle,
            lien: niveau.lien || null,
        })),
);
</script>

<style scoped>
.hierarchie {
    margin: 0;
}

.hierarchie__liste {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.3rem;
    margin: 0;
    padding: 0;
    list-style: none;
    font-size: 0.85rem;
}

.hierarchie__etape {
    display: flex;
    align-items: center;
    gap: 0.3rem;
}

.hierarchie__lien {
    color: var(--text-muted);
    font-weight: 500;
}

.hierarchie__lien:hover {
    color: var(--primary);
    text-decoration: underline;
}

.hierarchie__actuel {
    color: var(--text-main);
    font-weight: 600;
}

.hierarchie__separateur {
    color: var(--text-light);
}

@media (max-width: 640px) {
    .hierarchie__liste {
        font-size: 0.8rem;
    }
}
</style>
