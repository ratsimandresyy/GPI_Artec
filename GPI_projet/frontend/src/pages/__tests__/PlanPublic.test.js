import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import PlanPublic from '../PlanPublic.vue';

/*
 * Non-régression du cycle clavier de la fiche équipement.
 *
 * La fiche s'ouvre au clic sur un marqueur du plan. Elle doit entrer dans
 * le champ de vision par le focus, y maintenir la tabulation, se refermer
 * sur Échap, et rendre la main au marqueur qui l'a ouverte.
 *
 * Le plan est remplacé par un stub : le test porte sur la fiche et son
 * piège de focus, pas sur le rendu du plan lui-même.
 */

enableAutoUnmount(afterEach);

vi.mock('vue-router', () => ({
    useRoute: () => ({ query: {} }),
}));

vi.mock('../../services/batimentService', () => ({
    getBatiments: vi.fn().mockResolvedValue([{ id: 1, nom: 'Bâtiment A' }]),
}));

vi.mock('../../services/etageService', () => ({
    getEtages: vi.fn().mockResolvedValue([{ id: 10, batiment: 1, nom: 'RDC' }]),
}));

vi.mock('../../services/salleService', () => ({
    getSalles: vi.fn().mockResolvedValue([]),
}));

vi.mock('../../services/localisationService', () => ({
    getPlans: vi.fn().mockResolvedValue([{ id: 100, etage: 10, nom: 'Plan RDC' }]),
    getPositions: vi.fn().mockResolvedValue([]),
}));

vi.mock('../../services/dashboardService', () => ({
    getEquipementsDashboard: vi.fn().mockResolvedValue([]),
}));

/* Stub du plan : un bouton qui émet l'événement d'ouverture de la fiche. */
vi.mock('../../components/PlanViewer.vue', async () => {
    const { h } = await import('vue');

    /* Défini dans la factory : celle-ci s'exécute avant le corps du module. */
    const equipement = {
        id: 7,
        nom: 'Vidéoprojecteur',
        type: 'VIDEOPROJECTEUR',
        numero_inventaire: 'INV-0007',
        fabricant: 'Epson',
        modele: 'EB-L630U',
        etat: 'EN_SERVICE',
        situation: 'AFFECTE',
    };

    return {
        default: {
            name: 'PlanViewer',
            emits: ['equipement-clic'],
            setup(_props, { emit }) {
                return () =>
                    h(
                        'button',
                        {
                            id: 'marqueur',
                            onClick: () => emit('equipement-clic', equipement),
                        },
                        'Ouvrir la fiche'
                    );
            },
        },
    };
});

async function monter() {
    const wrapper = mount(PlanPublic, { attachTo: document.body });

    await flushPromises();

    /* Le plan n'est affiché qu'une fois bâtiment, étage et plan choisis. */
    await wrapper.find('#batiment-select').setValue('1');
    await wrapper.find('#etage-select').setValue('10');
    await wrapper.find('#plan-select').setValue('100');
    await flushPromises();

    return wrapper;
}

async function ouvrirFiche(wrapper) {
    const marqueur = wrapper.find('#marqueur');

    /* Le clic réel donne le focus au marqueur. */
    marqueur.element.focus();
    await marqueur.trigger('click');
    await flushPromises();
}

function appuiEchap() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
}

describe('PlanPublic.vue — fiche équipement', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('ouvre la fiche et y porte le focus', async () => {
        const wrapper = await monter();

        await ouvrirFiche(wrapper);

        const fiche = wrapper.find('[role="dialog"]');

        expect(fiche.exists()).toBe(true);
        expect(fiche.attributes('aria-modal')).toBe('true');
        expect(document.activeElement).toBe(fiche.element);
    });

    it('ferme la fiche avec la touche Échap', async () => {
        const wrapper = await monter();

        await ouvrirFiche(wrapper);
        expect(wrapper.find('[role="dialog"]').exists()).toBe(true);

        appuiEchap();
        await nextTick();

        expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
    });

    it('ferme la fiche au clic sur la croix', async () => {
        const wrapper = await monter();

        await ouvrirFiche(wrapper);

        await wrapper.find('.modal-fermeture').trigger('click');

        expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
    });

    it('emprisonne le focus dans la fiche', async () => {
        const wrapper = await monter();

        await ouvrirFiche(wrapper);

        const fiche = wrapper.find('[role="dialog"]').element;

        for (let i = 0; i < 6; i += 1) {
            document.dispatchEvent(
                new KeyboardEvent('keydown', {
                    key: 'Tab',
                    bubbles: true,
                    cancelable: true,
                })
            );
        }

        expect(fiche.contains(document.activeElement)).toBe(true);
    });

    it('rend le focus au marqueur à la fermeture', async () => {
        const wrapper = await monter();

        await ouvrirFiche(wrapper);

        const marqueur = wrapper.find('#marqueur').element;

        appuiEchap();
        await nextTick();

        expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
        expect(document.activeElement).toBe(marqueur);
    });
});
