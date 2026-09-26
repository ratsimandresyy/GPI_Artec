<template>
    <th
        class="sortable-header"
        @click="$emit('sort', key)"
    >
        {{ label }}
        <span v-if="currentSortKey === key" class="sort-icon">
            {{ currentSortOrder === 'asc' ? '↑' : '↓' }}
        </span>
        <span v-else class="sort-icon placeholder">↕</span>
    </th>
</template>

<script setup>
defineProps({
    key: {
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
</script>

<style scoped>
.sortable-header {
    cursor: pointer;
    user-select: none;
}

.sortable-header:hover {
    background: #f0f0f0;
}

.sort-icon {
    margin-left: 5px;
    font-size: 12px;
}

.sort-icon.placeholder {
    opacity: 0.3;
}
</style>
