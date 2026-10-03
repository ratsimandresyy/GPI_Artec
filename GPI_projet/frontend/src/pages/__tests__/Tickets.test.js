import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
    enableAutoUnmount,
    flushPromises,
    mount,
} from '@vue/test-utils';
import { nextTick } from 'vue';
import { createPinia, setActivePinia } from 'pinia';

import Tickets from '../Tickets.vue';
import { getTickets } from '../../services/ticketService';
import { getEquipementsDashboard } from '../../services/dashboardService';

/*
 * Non-régression de la fermeture clavier des deux modales de la page
 * des signalements (résolution et qualification).
 *
 * Ces modales n'utilisent pas d'écouteur sur leur overlay : la touche
 * Échap est traitée par `surTouche`, sur `document`, avec un garde-fou
 * sur l'état « enregistrement en cours ». Ces tests verrouillent ce
 * comportement existant, qui n'a pas été modifié par le lot 2.
 */

enableAutoUnmount(afterEach);

vi.mock('../../services/ticketService', () => ({
    getTickets: vi.fn(),
    creerTicket: vi.fn(),
    prendreEnChargeTicket: vi.fn(),
    resoudreTicket: vi.fn(),
    qualifierTicket: vi.fn(),
}));

vi.mock('../../services/dashboardService', () => ({
    getEquipementsDashboard: vi.fn(),
}));

vi.mock('../../stores/auth', () => ({
    useAuthStore: () => ({ isAdmin: true }),
}));

const TICKET = {
    id: 7,
    titre: 'Écran noir au démarrage',
    description: "L'écran ne s'allume plus.",
    equipement_nom: 'Vidéoprojecteur',
    equipement: 1,
    type: 'MAINTENANCE',
    priorite: 'NORMALE',
    statut: 'EN_COURS',
};

async function monter() {
    const pinia = createPinia();
    setActivePinia(pinia);

    const wrapper = mount(Tickets, {
        global: { plugins: [pinia] },
        attachTo: document.body,
    });

    await flushPromises();

    return wrapper;
}

function overlay(wrapper) {
    return wrapper.find('.modal-overlay');
}

function boutonAction(wrapper, libelle) {
    return wrapper.findAll('button').find((b) => b.text() === libelle);
}

async function ouvrirAction(wrapper, libelle) {
    const bouton = boutonAction(wrapper, libelle);

    expect(bouton, `bouton « ${libelle} » introuvable`).toBeTruthy();

    await bouton.trigger('click');
}

async function appuiEchap() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
    await nextTick();
}

function tabuler() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', {
            key: 'Tab',
            bubbles: true,
            cancelable: true,
        })
    );
}

describe('Tickets.vue — modales de résolution et de qualification', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.spyOn(console, 'error').mockImplementation(() => {});

        getTickets.mockResolvedValue([TICKET]);
        getEquipementsDashboard.mockResolvedValue([]);
    });

    it('ouvre la modale de résolution', async () => {
        const wrapper = await monter();

        expect(overlay(wrapper).exists()).toBe(false);

        await ouvrirAction(wrapper, 'Résoudre');

        expect(overlay(wrapper).exists()).toBe(true);
        expect(overlay(wrapper).text()).toContain(
            'Résoudre le signalement'
        );
        expect(overlay(wrapper).text()).toContain(
            'Écran noir au démarrage'
        );
    });

    it('ferme la modale de résolution avec Échap', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Résoudre');
        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('conserve la fermeture au clic extérieur de la résolution', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Résoudre');
        await overlay(wrapper).trigger('click');

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('ouvre la modale de qualification', async () => {
        const wrapper = await monter();

        expect(overlay(wrapper).exists()).toBe(false);

        await ouvrirAction(wrapper, 'Qualifier');

        expect(overlay(wrapper).exists()).toBe(true);
        expect(overlay(wrapper).text()).toContain(
            'Qualifier le signalement'
        );
    });

    it('ferme la modale de qualification avec Échap', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Qualifier');
        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('n\'ouvre pas les deux modales en même temps', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Résoudre');
        await appuiEchap();
        await ouvrirAction(wrapper, 'Qualifier');
        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('place le focus dans la modale de résolution à l\'ouverture', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Résoudre');

        /*
         * Sans cela, le focus restait sur le bouton du tableau, derrière
         * la modale, et la première tabulation repartait dans la liste.
         */
        expect(document.activeElement).toBe(
            wrapper.find('[role="dialog"]').element
        );
    });

    it('place le focus dans la modale de qualification à l\'ouverture', async () => {
        const wrapper = await monter();

        await ouvrirAction(wrapper, 'Qualifier');

        expect(document.activeElement).toBe(
            wrapper.find('[role="dialog"]').element
        );
    });

    it('emprisonne le focus dans la modale et le rend au bouton du tableau', async () => {
        const wrapper = await monter();
        const declencheur = boutonAction(wrapper, 'Résoudre');

        /* Le clic réel donne le focus au bouton cliqué. */
        declencheur.element.focus();
        await ouvrirAction(wrapper, 'Résoudre');

        const modale = wrapper.find('[role="dialog"]').element;

        /* Le focus ne doit jamais gagner les éléments de la liste. */
        for (let i = 0; i < 8; i += 1) {
            tabuler();
        }

        expect(modale.contains(document.activeElement)).toBe(true);

        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
        expect(document.activeElement).toBe(declencheur.element);
    });
});
