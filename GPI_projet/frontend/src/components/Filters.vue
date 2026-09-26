<template>
    <div class="filters">
        <div
            v-for="filter in filters"
            :key="filter.key"
            class="filter-item"
        >
            <label :for="filter.key">{{ filter.label }}</label>

            <select
                v-if="filter.type === 'select'"
                :id="filter.key"
                v-model="localFilters[filter.key]"
                @change="$emit('change', localFilters)"
            >
                <option value="">Tous</option>
                <option
                    v-for="option in filter.options"
                    :key="option.value"
                    :value="option.value"
                >
                    {{ option.label }}
                </option>
            </select>

            <input
                v-else-if="filter.type === 'text'"
                :id="filter.key"
                v-model="localFilters[filter.key]"
                type="text"
                :placeholder="filter.placeholder"
                @input="$emit('change', localFilters)"
            >
        </div>

        <button
            type="button"
            class="reset-button"
            @click="resetFilters"
        >
            Réinitialiser
        </button>
    </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
    filters: {
        type: Array,
        required: true
    },
    initialFilters: {
        type: Object,
        default: () => ({})
    }
});

const emit = defineEmits(['change', 'reset']);

const localFilters = ref({ ...props.initialFilters });

watch(() => props.initialFilters, (newFilters) => {
    localFilters.value = { ...newFilters };
}, { deep: true });

function resetFilters() {
    const resetFilters = {};
    props.filters.forEach(filter => {
        resetFilters[filter.key] = '';
    });
    localFilters.value = resetFilters;
    emit('reset', resetFilters);
}
</script>

<style scoped>
.filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 20px;
}

.filter-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.filter-item label {
    font-size: 12px;
    font-weight: 600;
    color: #666;
}

.filter-item select,
.filter-item input {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    min-width: 150px;
}

.reset-button {
    padding: 8px 16px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: white;
    cursor: pointer;
    align-self: flex-end;
}

.reset-button:hover {
    background: #f0f0f0;
}
</style>
