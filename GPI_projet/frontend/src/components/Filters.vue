<template>
    <section
        class="filtres"
        aria-label="Recherche et filtres"
    >
        <div class="filtres__entete">
            <h2 class="filtres__titre">
                Recherche et filtres
            </h2>

            <!--
                Le compteur indique combien de filtres sont réellement
                actifs : sans lui, un résultat restreint est
                indiscernable d'un parc volontairement réduit.
            -->
            <p
                v-if="nombreFiltresActifs > 0"
                class="filtres__actifs"
                role="status"
            >
                {{ nombreFiltresActifs }} filtre(s) actif(s)
            </p>
        </div>

        <div class="filtres__corps">
            <div
                v-for="filter in filters"
                :key="filter.key"
                class="filtres__champ"
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
                    type="search"
                    :placeholder="filter.placeholder"
                    @input="$emit('change', localFilters)"
                >
            </div>

            <button
                type="button"
                class="btn-ghost btn-sm filtres__reinitialiser"
                :disabled="nombreFiltresActifs === 0"
                @click="reinitialiser"
            >
                Réinitialiser
            </button>
        </div>
    </section>
</template>

<script setup>
/**
 * Zone de recherche et de filtres.
 *
 * Les contrôles sont regroupés dans un seul bloc afin que la
 * recherche et les filtres se lisent comme un ensemble, et non comme
 * des éléments dispersés dans la page.
 *
 * Le composant ne filtre rien : il publie les valeurs saisies et laisse
 * la page piloter le filtrage. Il ne valide pas non plus les données,
 * cette responsabilité reste celle de l'API.
 */
import { ref, computed, watch } from 'vue';

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

const nombreFiltresActifs = computed(
    () => props.filters.filter(
        (filter) => String(localFilters.value[filter.key] || '').trim() !== ''
    ).length
);

function reinitialiser() {
    const valeursVides = {};
    props.filters.forEach((filter) => {
        valeursVides[filter.key] = '';
    });

    localFilters.value = valeursVides;
    emit('reset', valeursVides);
}
</script>

<style scoped>
.filtres {
    padding: 0.9rem 1rem 1rem;
    background-color: var(--bg-surface);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}

.filtres__entete {
    display: flex;
    flex-wrap: wrap;
    align-items: baseline;
    justify-content: space-between;
    gap: 0.5rem;
    margin-bottom: 0.75rem;
}

.filtres__titre {
    margin: 0;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: var(--text-muted);
}

.filtres__actifs {
    margin: 0;
    padding: 0.1rem 0.5rem;
    border-radius: var(--radius-full);
    background-color: var(--primary-light);
    border: 1px solid var(--primary-focus);
    color: var(--primary);
    font-size: 0.75rem;
    font-weight: 600;
}

.filtres__corps {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    gap: 0.75rem;
}

.filtres__champ {
    display: flex;
    flex: 1 1 190px;
    flex-direction: column;
    gap: 0.3rem;
    min-width: 0;
}

.filtres__champ label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--text-muted);
}

/*
 * `input[type=search]` ajoute un bouton d'effacement propriétaire ;
 * on le masque au profit de notre bouton « Réinitialiser ».
 */
.filtres__champ input[type='search']::-webkit-search-cancel-button {
    appearance: none;
}

.filtres__reinitialiser {
    flex: 0 0 auto;
}

@media (max-width: 640px) {
    .filtres__champ {
        flex: 1 1 100%;
    }

    .filtres__reinitialiser {
        width: 100%;
    }
}
</style>
