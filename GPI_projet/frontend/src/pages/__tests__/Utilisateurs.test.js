import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { nextTick } from 'vue';
import { createPinia, setActivePinia } from 'pinia';

import Utilisateurs from '../Utilisateurs.vue';
import { getUtilisateurs } from '../../services/utilisateurService';

/*
 * Non-régression de la fermeture au clavier du formulaire utilisateur.
 *
 * Le voile `.modal-overlay` n'est pas focusable et reste décoratif :
 * la fermeture au clavier passe par l'écouteur `document`, sur le
 * modèle de `MainLayout.vue` et `Tickets.vue`.
 */

vi.mock('../../services/utilisateurService', () => ({
    getUtilisateurs: vi.fn(),
    creerUtilisateur: vi.fn(),
    modifierUtilisateur: vi.fn(),
    supprimerUtilisateur: vi.fn(),
}));

vi.mock('../../stores/auth', () => ({
    useAuthStore: () => ({ isAdmin: true }),
}));

async function monter({ attache = false } = {}) {
    const pinia = createPinia();
    setActivePinia(pinia);

    const wrapper = mount(Utilisateurs, {
        global: { plugins: [pinia] },
        /*
         * Le focus n'est réellement distribuable que si le composant est
         * attaché au document : `mount` seul travaille dans le vide.
         */
        attachTo: attache ? document.body : undefined,
    });

    await flushPromises();

    return wrapper;
}

function overlay(wrapper) {
    return wrapper.find('.modal-overlay');
}

async function ouvrirFormulaire(wrapper) {
    const bouton = wrapper
        .findAll('button')
        .find((b) => b.text() === 'Nouvel utilisateur');

    expect(bouton, 'bouton « Nouvel utilisateur » introuvable').toBeTruthy();

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

describe('Utilisateurs.vue — formulaire en modale', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.spyOn(console, 'error').mockImplementation(() => {});

        getUtilisateurs.mockResolvedValue([]);
    });

    it('ouvre le formulaire au clic', async () => {
        const wrapper = await monter();

        expect(overlay(wrapper).exists()).toBe(false);

        await ouvrirFormulaire(wrapper);

        expect(overlay(wrapper).exists()).toBe(true);
        expect(overlay(wrapper).text()).toContain('Créer un utilisateur');
    });

    it('ferme le formulaire avec la touche Échap', async () => {
        const wrapper = await monter();

        await ouvrirFormulaire(wrapper);
        expect(overlay(wrapper).exists()).toBe(true);

        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('conserve la fermeture au clic sur le voile', async () => {
        const wrapper = await monter();

        await ouvrirFormulaire(wrapper);

        /* `.self` : le clic sur le voile lui-même ferme, pas un clic interne. */
        await overlay(wrapper).trigger('click');

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('ignore Échap quand aucun formulaire n\'est ouvert', async () => {
        const wrapper = await monter();

        expect(overlay(wrapper).exists()).toBe(false);

        await appuiEchap();

        expect(overlay(wrapper).exists()).toBe(false);
    });

    it('emprisonne le focus dans le formulaire et le rend au déclencheur', async () => {
        const wrapper = await monter({ attache: true });

        const declencheur = wrapper
            .findAll('button')
            .find((b) => b.text() === 'Nouvel utilisateur');

        /* Le clic réel donne le focus au bouton cliqué. */
        declencheur.element.focus();
        await declencheur.trigger('click');
        await flushPromises();

        const modale = wrapper.find('[role="dialog"]').element;

        /* Le focus entre dans la modale, sur la boîte entière. */
        expect(document.activeElement).toBe(modale);

        /* Plusieurs tabulations restent piégées dans le formulaire. */
        for (let i = 0; i < 6; i += 1) {
            tabuler();
        }

        expect(modale.contains(document.activeElement)).toBe(true);

        /* Fermeture : le focus revient sur le bouton du tableau. */
        await appuiEchap();
        await flushPromises();

        expect(overlay(wrapper).exists()).toBe(false);
        expect(document.activeElement).toBe(declencheur.element);
    });
});
