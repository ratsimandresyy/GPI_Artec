import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
    enableAutoUnmount,
    flushPromises,
    mount,
} from '@vue/test-utils';
import { nextTick } from 'vue';

import EquipementForm from '../EquipementForm.vue';
import { getSalles } from '../../services/salleService';

/*
 * Non-régression du clavier dans la modale d'équipement.
 *
 * Échap était attaché à la boîte, qui n'est pas focusable : il ne se
 * déclenchait que si le focus se trouvait déjà dans le formulaire.
 * L'écoute est désormais portée par `document`, et la boîte reçoit le
 * focus à l'ouverture.
 *
 * Le montage est attaché au document : sans cela, aucun élément ne peut
 * réellement recevoir le focus.
 */

enableAutoUnmount(afterEach);

vi.mock('../../services/salleService', () => ({
    getSalles: vi.fn(),
}));

async function monter(props = {}) {
    const wrapper = mount(EquipementForm, {
        props,
        attachTo: document.body,
    });

    await flushPromises();

    return wrapper;
}

async function appuiEchap() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
    await nextTick();
}

function boite(wrapper) {
    return wrapper.find('[role="dialog"]');
}

describe('EquipementForm.vue — clavier et contrôles', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.spyOn(console, 'error').mockImplementation(() => {});

        getSalles.mockResolvedValue([]);
    });

    it('ferme avec Échap même si le focus est hors du formulaire', async () => {
        const wrapper = await monter();

        /*
         * C'est précisément le cas qui échouait : le focus placé
         * ailleurs ne remontait jamais jusqu'à la boîte.
         */
        const horsFormulaire = document.createElement('button');
        document.body.appendChild(horsFormulaire);
        horsFormulaire.focus();

        expect(document.activeElement).toBe(horsFormulaire);

        await appuiEchap();

        expect(wrapper.emitted('close')).toHaveLength(1);

        horsFormulaire.remove();
    });

    it('ferme avec Échap depuis un champ du formulaire', async () => {
        const wrapper = await monter();

        await wrapper.find('#equipement-nom').element.focus();
        await appuiEchap();

        expect(wrapper.emitted('close')).toHaveLength(1);
    });

    it("n'émet pas de fermeture pendant l'enregistrement", async () => {
        const wrapper = await monter({ chargement: true });

        await appuiEchap();

        expect(wrapper.emitted('close')).toBeUndefined();
    });

    it('place le focus dans la boîte à l\'ouverture', async () => {
        const wrapper = await monter();

        expect(document.activeElement).toBe(boite(wrapper).element);
        expect(boite(wrapper).attributes('tabindex')).toBe('-1');
    });

    it('ne place pas la boîte dans l\'ordre de tabulation', async () => {
        const wrapper = await monter();

        /*
         * `tabindex="-1"` rend la boîte programmable sans créer un point
         * d'arrêt : la tabulation doit entrer par le premier champ.
         */
        const ordre = wrapper
            .findAll('button, input, select, textarea')
            .map((el) => el.attributes('id') || el.text().trim());

        expect(ordre[0]).toBe('equipement-nom');
        expect(ordre).not.toContain('');
    });

    it('associe chaque étiquette à son champ', async () => {
        const wrapper = await monter();

        const champs = wrapper.findAll('input, select, textarea');

        expect(champs.length).toBeGreaterThan(0);

        champs.forEach((champ) => {
            const id = champ.attributes('id');

            expect(id, 'un champ sans identifiant').toBeTruthy();
            expect(
                wrapper.find(`label[for="${id}"]`).exists(),
                `aucune étiquette pour #${id}`
            ).toBe(true);
        });
    });

    it('donne un nom accessible à chaque bouton', async () => {
        const wrapper = await monter();

        const boutons = wrapper.findAll('button');

        expect(boutons.length).toBeGreaterThan(0);

        boutons.forEach((bouton) => {
            const texte = bouton.text().trim();
            const nom = bouton.attributes('aria-label');

            /* Aucun bouton réduit à une icône sans nom. */
            expect(texte !== '' || nom).toBeTruthy();
        });
    });
});
