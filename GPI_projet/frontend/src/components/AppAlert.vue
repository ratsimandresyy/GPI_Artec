<template>
    <div
        class="alert"
        :class="`alert--${type}`"
        :role="role"
    >
        <span
            class="alert__icon"
            aria-hidden="true"
        >
            {{ icone }}
        </span>

        <div class="alert__body">
            <slot>
                {{ message }}
            </slot>
        </div>
    </div>
</template>

<script setup>
import { computed } from "vue";

/**
 * Message d'état en ligne : information, succès, avertissement, erreur.
 *
 * L'information n'est jamais portée par la couleur seule : chaque
 * type possède un symbole et, pour les erreurs, un rôle ARIA.
 */
const props = defineProps({
    type: {
        type: String,
        default: "info",
        validator: (valeur) =>
            ["info", "success", "warning", "error"].includes(valeur),
    },

    message: {
        type: String,
        default: "",
    },
});

const ICONES = {
    info: "i",
    success: "✓",
    warning: "!",
    error: "✕",
};

const icone = computed(() => ICONES[props.type] || "i");

const role = computed(() =>
    props.type === "error" ? "alert" : "status",
);
</script>
