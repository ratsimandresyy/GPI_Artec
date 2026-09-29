<template>
    <nav
        v-if="totalItems > 0"
        class="pagination"
        aria-label="Pagination des résultats"
    >
        <button
            type="button"
            class="pagination__bouton"
            :disabled="currentPage <= 1"
            @click="$emit('change', currentPage - 1)"
        >
            <span aria-hidden="true">←</span>
            Précédent
        </button>

        <span class="pagination__info">
            Page
            <strong>{{ currentPage }}</strong>
            sur
            <strong>{{ totalPages }}</strong>
            <span class="pagination__total">
                ({{ totalItems }} élément{{ totalItems > 1 ? 's' : '' }})
            </span>
        </span>

        <button
            type="button"
            class="pagination__bouton"
            :disabled="currentPage >= totalPages"
            @click="$emit('change', currentPage + 1)"
        >
            Suivant
            <span aria-hidden="true">→</span>
        </button>

        <label class="pagination__taille">
            <span class="visually-hidden">
                Nombre d'éléments par page
            </span>

            <select
                v-model="pageSizeModel"
                class="pagination__select"
            >
                <option :value="10">10 / page</option>
                <option :value="25">25 / page</option>
                <option :value="50">50 / page</option>
                <option :value="100">100 / page</option>
            </select>
        </label>
    </nav>
</template>

<script setup>
/**
 * Pagination d'un tableau de résultats.
 *
 * Le composant ne gère que l'affichage et publie l'intention de
 * changer de page ou de taille : la pagination elle-même est
 * appliquée par la page, via le composable de table.
 *
 * Rien n'est rendu si la liste est vide : une pagination sans résultat
 * n'a rien à paginer.
 */
import { computed } from 'vue';

const props = defineProps({
    currentPage: {
        type: Number,
        required: true
    },
    pageSize: {
        type: Number,
        required: true
    },
    totalItems: {
        type: Number,
        required: true
    }
});

const emit = defineEmits(['change', 'page-size-change']);

const totalPages = computed(
    () => Math.max(1, Math.ceil(props.totalItems / props.pageSize))
);

const pageSizeModel = computed({
    get: () => props.pageSize,
    set: (value) => emit('page-size-change', parseInt(value))
});
</script>

<style scoped>
.pagination {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
    padding-top: 0.5rem;
}

.pagination__bouton {
    padding: 0.45rem 0.85rem;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--secondary);
    background-color: var(--bg-surface);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.15s ease-in-out;
}

.pagination__bouton:hover:not(:disabled) {
    background-color: var(--bg-subtle);
    border-color: var(--text-muted);
    color: var(--text-main);
}

.pagination__bouton:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination__info {
    color: var(--text-muted);
    font-size: 0.875rem;
}

.pagination__total {
    color: var(--text-light);
}

.pagination__select {
    padding: 0.4rem 0.6rem;
    font-size: 0.8125rem;
    font-family: inherit;
    color: var(--text-main);
    background-color: var(--bg-surface);
    border: 1px solid var(--border-medium);
    border-radius: var(--radius-md);
    cursor: pointer;
}

@media (max-width: 640px) {
    .pagination {
        justify-content: center;
    }

    .pagination__total {
        display: none;
    }
}
</style>
