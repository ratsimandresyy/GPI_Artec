<template>
    <div
        class="state-block"
        role="status"
        aria-live="polite"
    >
        <span
            class="spinner"
            aria-hidden="true"
        />

        <p class="state-block__title">
            {{ titre }}
        </p>

        <p
            v-if="message"
            class="state-block__text"
        >
            {{ message }}
        </p>
    </div>
</template>

<script setup>
/**
 * Affichage normalisé d'un chargement en cours.
 *
 * `role="status"` et `aria-live` permettent aux lecteurs d'écran
 * d'annoncer l'état sans dépendre de la couleur ou du spinner.
 */
defineProps({
    titre: {
        type: String,
        default: "Chargement en cours…",
    },

    message: {
        type: String,
        default: "",
    },
});
</script>
