<template>
    <div class="state-block">
        <span
            class="state-block__icon"
            aria-hidden="true"
        >
            <svg
                viewBox="0 0 24 24"
                width="30"
                height="30"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <path d="M3 7h18M3 12h18M3 17h10" />
            </svg>
        </span>

        <p class="state-block__title">
            {{ titre }}
        </p>

        <p
            v-if="message"
            class="state-block__text"
        >
            {{ message }}
        </p>

        <slot />
    </div>
</template>

<script setup>
/**
 * Affichage normalisé d'un résultat vide.
 *
 * L'icône est décorative : l'information utile est le titre,
 * toujours présent en texte.
 */
defineProps({
    titre: {
        type: String,
        default: "Aucun résultat.",
    },

    message: {
        type: String,
        default: "",
    },
});
</script>
