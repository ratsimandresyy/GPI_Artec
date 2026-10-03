import { beforeEach, describe, expect, it, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import Login from '../Login.vue';
import { useAuthStore } from '../../stores/auth';

/*
 * Non-régression du parcours clavier de l'écran de connexion.
 *
 * L'`autofocus` a été retiré : il vole le focus au titre de la page,
 * qu'un lecteur d'écran doit pouvoir lire avant le formulaire. L'ordre
 * de tabulation suit désormais l'ordre visuel, que ce test verrouille.
 */

const router = { push: vi.fn() };

vi.mock('vue-router', () => ({
    useRouter: () => router,
}));

const seConnecter = vi.fn();
const seDeconnecter = vi.fn();

vi.mock('../../stores/auth', () => ({
    useAuthStore: () => ({
        seConnecter,
        seDeconnecter,
        user: { role: 'ADMIN' },
    }),
}));

function monter() {
    return mount(Login);
}

/*
 * jsdom n'implémente pas la navigation au Tab : on vérifie l'ordre
 * dans le DOM, qui est exactement celui que suit la tabulation.
 */
function ordreFocusable(wrapper) {
    return wrapper
        .findAll('button, input')
        .map((el) => el.attributes('id') || el.text().trim());
}

describe('Login.vue — parcours clavier', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        seConnecter.mockResolvedValue(undefined);
    });

    it("n'utilise plus d'autofocus", async () => {
        const wrapper = monter();

        await nextTick();

        expect(
            wrapper.find('#username').attributes('autofocus')
        ).toBeUndefined();
    });

    it('suit l\'ordre visuel pour la tabulation', async () => {
        const wrapper = monter();

        await nextTick();

        expect(ordreFocusable(wrapper)).toEqual([
            '← Retour',
            'username',
            'password',
            'Se connecter',
        ]);
    });

    it('associe chaque champ à son étiquette', async () => {
        const wrapper = monter();

        await nextTick();

        expect(wrapper.find('label[for="username"]').exists()).toBe(true);
        expect(wrapper.find('label[for="password"]').exists()).toBe(true);
    });

    it('soumet le formulaire sans modifier l\'authentification', async () => {
        const wrapper = monter();

        await wrapper.find('#username').setValue('admin');
        await wrapper.find('#password').setValue('secret');
        await wrapper.find('form').trigger('submit');
        await nextTick();

        expect(seConnecter).toHaveBeenCalledWith('admin', 'secret');
        expect(router.push).toHaveBeenCalledWith('/dashboard');
    });
});
