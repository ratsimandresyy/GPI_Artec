<template>
    <div
        class="modal-overlay"
        @click.self="annuler"
    >
        <div
            class="confirm"
            role="alertdialog"
            aria-modal="true"
            :aria-labelledby="titreId"
            :aria-describedby="messageId"
        >
            <h2
                :id="titreId"
                class="confirm__titre"
            >
                {{ titre }}
            </h2>

            <p
                :id="messageId"
                class="confirm__message"
            >
                <slot>{{ message }}</slot>
            </p>

            <p
                v-if="consequence"
                class="confirm__consequence"
            >
                {{ consequence }}
            </p>

            <div class="confirm__actions">
                <button
                    ref="boutonAnnuler"
                    type="button"
                    class="btn-secondary"
                    :disabled="enCours"
                    @click="annuler"
                >
                    {{ libelleAnnulation }}
                </button>

                <button
                    type="button"
                    :class="danger ? 'btn-delete' : 'btn-primary'"
                    :disabled="enCours"
                    @click="confirmer"
                >
                    {{ enCours ? 'Traitement…' : libelleConfirmation }}
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
/**
 * Confirmation explicite avant une suppression.
 *
 * Remplace `window.confirm`, dont le message est unique, non stylé
 * et peu explicite sur ce qui va réellement disparaître. Cette boîte
 * nomme l'objet concerné et énonce la conséquence.
 *
 * Le composant ne porte aucune règle métier : il demande l'accord de
 * l'utilisateur. La suppression reste déclenchée par la page
 * appelante et l'autorisation effective reste assurée par l'API.
 */
import { nextTick, ref, onMounted, onBeforeUnmount } from "vue";

const props = defineProps({
    // Titre de la boîte, par exemple « Supprimer l'équipement ».
    titre: {
        type: String,
        required: true,
    },

    // Ce qui va être supprimé, nommé explicitement.
    message: {
        type: String,
        default: "",
    },

    // Conséquence distincte de la disparition de l'objet.
    consequence: {
        type: String,
        default: "",
    },

    libelleConfirmation: {
        type: String,
        default: "Supprimer",
    },

    libelleAnnulation: {
        type: String,
        default: "Annuler",
    },

    // `true` pour un bouton rouge. Réservé aux actions destructrices.
    danger: {
        type: Boolean,
        default: true,
    },
});

const emit = defineEmits(["confirm", "cancel"]);

const enCours = ref(false);
const boutonAnnuler = ref(null);

// Identifiants du titre et du message, nécessaires aux relations
// aria-labelledby / aria-describedby.
const suffixe = Math.random().toString(36).slice(2, 8);
const titreId = `confirmation-titre-${suffixe}`;
const messageId = `confirmation-message-${suffixe}`;

function annuler() {
    if (enCours.value) {
        return;
    }

    emit("cancel");
}

function confirmer() {
    enCours.value = true;
    emit("confirm");
}

/*
 * Échap ferme la boîte. L'écoute se fait sur `document` car le focus
 * peut se trouver dans la boîte comme dans la page sous-jacente.
 */
function surTouche(event) {
    if (event.key === "Escape") {
        annuler();
    }
}

onMounted(async () => {
    document.addEventListener("keydown", surTouche);

    /*
     * Le focus revient sur l'annulation : l'utilisateur peut quitter
     * la boîte au clavier sans valider une suppression par inadvertance.
     */
    await nextTick();
    boutonAnnuler.value?.focus();
});

onBeforeUnmount(() => {
    document.removeEventListener("keydown", surTouche);
});
</script>

<style scoped>
.confirm {
    width: 100%;
    max-width: 460px;
    padding: 1.5rem;
    background-color: var(--bg-surface);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
}

.confirm__titre {
    margin: 0 0 0.6rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--text-main);
}

.confirm__message {
    margin: 0 0 0.75rem;
    color: var(--text-main);
    font-size: 0.9rem;
}

.confirm__consequence {
    margin: 0 0 1.1rem;
    padding: 0.65rem 0.8rem;
    background-color: var(--danger-light);
    border: 1px solid rgba(220, 38, 38, 0.25);
    border-radius: var(--radius-md);
    color: var(--danger-text);
    font-size: 0.85rem;
}

.confirm__actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 0.5rem;
}

@media (max-width: 640px) {
    .confirm__actions {
        flex-direction: column-reverse;
    }

    .confirm__actions > * {
        width: 100%;
    }
}
</style>
