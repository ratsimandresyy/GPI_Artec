<template>
    <th
        class="sortable-header"
        scope="col"
        :aria-sort="ariaSort"
    >
        <button
            type="button"
            class="sortable-header__button"
            :aria-label="ariaLabel"
            @click="$emit('sort', columnKey)"
        >
            <span>{{ label }}</span>

            <span
                class="sort-icon"
                :class="{
                    'sort-icon--placeholder': !estColonneActive
                }"
                aria-hidden="true"
            >
                {{ symbole }}
            </span>
        </button>
    </th>
</template>

<script setup>
/**
 * En-tête de colonne triable.
 *
 * Le tri est porté par un vrai <button> : la colonne reste ainsi
 * opérable au clavier et annoncée correctement, ce qu'un <th @click>
 * ne permettait pas.
 *
 * L'indicateur visuel est doublé d'un liaellé lisible par les lecteurs
 * d'écran, l'information n'est donc jamais portée par la seule couleur.
 */
import { computed } from "vue";

const props = defineProps({
    // 'key' est un nom réservé par Vue : on utilise columnKey.
    columnKey: {
        type: String,
        required: true
    },
    label: {
        type: String,
        required: true
    },
    currentSortKey: {
        type: String,
        default: ''
    },
    currentSortOrder: {
        type: String,
        default: 'asc'
    }
});

defineEmits(['sort']);

const estColonneActive = computed(
    () => props.currentSortKey === props.columnKey
);

const symbole = computed(() => {
    if (!estColonneActive.value) {
        return '↕';
    }

    return props.currentSortOrder === 'asc' ? '↑' : '↓';
});

const ariaSort = computed(() => {
    if (!estColonneActive.value) {
        return 'none';
    }

    return props.currentSortOrder === 'asc' ? 'ascending' : 'descending';
});

const ariaLabel = computed(() => {
    if (!estColonneActive.value) {
        return `Trier par ${props.label}`;
    }

    const sens = props.currentSortOrder === 'asc'
        ? 'ordre croissant'
        : 'ordre décroissant';

    return `${props.label}, trié par ${sens}. Changer le tri.`;
});
</script>

<style scoped>
.sortable-header {
    padding: 0;
    white-space: nowrap;
}

.sortable-header__button {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    width: 100%;
    padding: 0.75rem 1rem;
    background: none;
    border: none;
    font-size: 0.75rem;
    font-weight: 700;
    line-height: 1.25rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    text-align: left;
    color: inherit;
    cursor: pointer;
    user-select: none;
}

.sortable-header__button:hover {
    background-color: var(--primary-light);
}

.sort-icon {
    font-size: 12px;
    line-height: 1;
}

.sort-icon--placeholder {
    opacity: 0.4;
}
</style>
