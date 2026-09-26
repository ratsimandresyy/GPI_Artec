<template>
    <div class="pagination">
        <button
            type="button"
            class="pagination-button"
            :disabled="currentPage === 1"
            @click="$emit('change', currentPage - 1)"
        >
            ← Précédent
        </button>

        <span class="pagination-info">
            Page {{ currentPage }} / {{ totalPages }} ({{ totalItems }} éléments)
        </span>

        <button
            type="button"
            class="pagination-button"
            :disabled="currentPage === totalPages"
            @click="$emit('change', currentPage + 1)"
        >
            Suivant →
        </button>

        <select
            v-model="pageSizeModel"
            class="pagination-page-size"
            @change="$emit('page-size-change', $event.target.value)"
        >
            <option :value="10">10 / page</option>
            <option :value="25">25 / page</option>
            <option :value="50">50 / page</option>
            <option :value="100">100 / page</option>
        </select>
    </div>
</template>

<script setup>
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

const totalPages = computed(() => Math.ceil(props.totalItems / props.pageSize));

const pageSizeModel = computed({
    get: () => props.pageSize,
    set: (value) => emit('page-size-change', parseInt(value))
});
</script>

<style scoped>
.pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 15px;
    padding: 20px 0;
}

.pagination-button {
    padding: 8px 16px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: white;
    cursor: pointer;
}

.pagination-button:hover:not(:disabled) {
    background: #f0f0f0;
}

.pagination-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.pagination-info {
    font-size: 14px;
    color: #666;
}

.pagination-page-size {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: white;
    cursor: pointer;
}
</style>
