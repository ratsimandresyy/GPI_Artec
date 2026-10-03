import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import MainLayout from '../MainLayout.vue';

/*
 * Non-régression de la fermeture au clavier du menu mobile.
 *
 * Le voile `.sidebar-backdrop` n'est pas focusable et reste décoratif :
 * la fermeture au clavier passe donc par un écouteur sur `document`,
 * comme dans les autres modales de l'application.
 */

vi.mock('vue-router', () => ({
    useRoute: () => ({ fullPath: '/dashboard' }),
    useRouter: () => ({ push: vi.fn() }),
}));

vi.mock('../../stores/auth', () => ({
    useAuthStore: () => ({
        user: { username: 'admin', role: 'ADMIN' },
        seDeconnecter: vi.fn(),
    }),
}));

/* Le voile ne s'affiche que lorsque le menu est ouvert. */
function voile(wrapper) {
    return wrapper.find('.sidebar-backdrop');
}

function ouvrirMenu(wrapper) {
    return wrapper.find('.topbar__toggle').trigger('click');
}

async function appuiEchap() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
    await nextTick();
}

async function monter() {
    const wrapper = mount(MainLayout, {
        global: {
            stubs: {
                RouterLink: true,
                NotificationToast: true,
            },
        },
    });

    await nextTick();

    return wrapper;
}

describe('MainLayout.vue — menu mobile', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('ouvre le menu au clic sur le bouton', async () => {
        const wrapper = await monter();

        expect(voile(wrapper).exists()).toBe(false);

        await ouvrirMenu(wrapper);

        expect(voile(wrapper).exists()).toBe(true);
        expect(
            wrapper.find('.topbar__toggle').attributes('aria-expanded')
        ).toBe('true');
    });

    it('ferme le menu avec la touche Échap', async () => {
        const wrapper = await monter();

        await ouvrirMenu(wrapper);
        expect(voile(wrapper).exists()).toBe(true);

        await appuiEchap();

        expect(voile(wrapper).exists()).toBe(false);
        expect(
            wrapper.find('.topbar__toggle').attributes('aria-expanded')
        ).toBe('false');
    });

    it('conserve la fermeture au clic sur le voile', async () => {
        const wrapper = await monter();

        await ouvrirMenu(wrapper);
        await voile(wrapper).trigger('click');

        expect(voile(wrapper).exists()).toBe(false);
    });

    it('ignore Échap quand le menu est déjà fermé', async () => {
        const wrapper = await monter();

        expect(voile(wrapper).exists()).toBe(false);

        /* Aucun effet, et surtout aucune erreur. */
        await appuiEchap();

        expect(voile(wrapper).exists()).toBe(false);
    });
});
