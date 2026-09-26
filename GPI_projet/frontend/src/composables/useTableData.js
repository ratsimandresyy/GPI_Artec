import { ref, computed } from 'vue';

export function useTableData(items, options = {}) {
    const currentPage = ref(1);
    const pageSize = ref(options.defaultPageSize || 25);
    const sortKey = ref(options.defaultSortKey || '');
    const sortOrder = ref(options.defaultSortOrder || 'asc');
    const filters = ref(options.defaultFilters || {});

    const filteredItems = computed(() => {
        let result = [...items.value];

        // Appliquer les filtres
        Object.entries(filters.value).forEach(([key, value]) => {
            if (value) {
                result = result.filter(item => {
                    if (key.includes('.')) {
                        const keys = key.split('.');
                        let itemValue = item;
                        for (const k of keys) {
                            itemValue = itemValue?.[k];
                        }
                        return String(itemValue).toLowerCase().includes(String(value).toLowerCase());
                    }
                    return String(item[key]).toLowerCase().includes(String(value).toLowerCase());
                });
            }
        });

        // Appliquer le tri
        if (sortKey.value) {
            result.sort((a, b) => {
                let aVal = a[sortKey.value];
                let bVal = b[sortKey.value];

                if (typeof aVal === 'string') aVal = aVal.toLowerCase();
                if (typeof bVal === 'string') bVal = bVal.toLowerCase();

                if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1;
                if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1;
                return 0;
            });
        }

        return result;
    });

    const totalPages = computed(() => Math.ceil(filteredItems.value.length / pageSize.value));

    const paginatedItems = computed(() => {
        const start = (currentPage.value - 1) * pageSize.value;
        const end = start + pageSize.value;
        return filteredItems.value.slice(start, end);
    });

    function setPage(page) {
        if (page >= 1 && page <= totalPages.value) {
            currentPage.value = page;
        }
    }

    function setPageSize(size) {
        pageSize.value = size;
        currentPage.value = 1;
    }

    function setSort(key) {
        if (sortKey.value === key) {
            sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc';
        } else {
            sortKey.value = key;
            sortOrder.value = 'asc';
        }
    }

    function setFilter(key, value) {
        filters.value = { ...filters.value, [key]: value };
        currentPage.value = 1;
    }

    function setFilters(newFilters) {
        filters.value = { ...newFilters };
        currentPage.value = 1;
    }

    function resetFilters() {
        filters.value = {};
        currentPage.value = 1;
    }

    return {
        currentPage,
        pageSize,
        sortKey,
        sortOrder,
        filters,
        filteredItems,
        paginatedItems,
        totalPages,
        setPage,
        setPageSize,
        setSort,
        setFilter,
        setFilters,
        resetFilters
    };
}
