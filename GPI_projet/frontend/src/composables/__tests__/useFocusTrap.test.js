import { afterEach, describe, expect, it } from 'vitest';
import { enableAutoUnmount, flushPromises, mount } from '@vue/test-utils';
import { defineComponent, h, nextTick, reactive, ref } from 'vue';

import { useFocusTrap } from '../useFocusTrap';

/*
 * Non-régression du piège de focus partagé.
 *
 * Le composable impose trois garanties aux modales : le focus entre à
 * l'ouverture, il ne sort plus par `Tab` tant qu'elles sont visibles, et
 * il revient sur le déclencheur à la fermeture. Il n'intercepte que
 * `Tab` : `Escape` et les règles métier des composants restent intacts.
 *
 * Le montage est attaché au document : sans cela, aucun élément ne peut
 * réellement recevoir le focus et les assertions seraient toujours fausses.
 */

enableAutoUnmount(afterEach);

/*
 * Page pilote : un déclencheur, un élément focusable « derrière » la
 * modale, et une modale dont le contenu focusable est paramétrable.
 *
 * Le composable est appelé dans le `setup` de la modale, comme dans le
 * code réel, et la référence est liée par fermeture : c'est la seule
 * façon d'obtenir le ref brut, que l'accès par `this.x` dénuderait.
 */
function creerHote(reglages = {}) {
    const etat = reactive({ ouvert: false, supplement: false, ...reglages });

    const Modale = defineComponent({
        name: 'ModaleTest',
        setup() {
            const modale = ref(null);

            useFocusTrap(modale, { focusInitial: etat.focusInitial });

            return () =>
                h('div', { class: 'modal-overlay' }, [
                    h(
                        'div',
                        { ref: modale, class: 'modal', role: 'dialog', tabindex: '-1' },
                        [
                            etat.vide ? null : h('button', { id: 'premier' }, 'Premier'),
                            etat.vide ? null : h('button', { id: 'milieu' }, 'Milieu'),
                            etat.vide ? null : h('button', { id: 'dernier' }, 'Dernier'),
                            etat.desactive
                                ? h(
                                      'button',
                                      { id: 'desactive', disabled: true },
                                      'Désactivé'
                                  )
                                : null,
                            etat.masque
                                ? h('button', { id: 'masque', hidden: true }, 'Masqué')
                                : null,
                            etat.supplement
                                ? h('button', { id: 'supplement' }, 'Ajouté')
                                : null,
                        ]
                    ),
                ]);
        },
    });

    const Hote = defineComponent({
        name: 'HoteTest',
        setup() {
            return { etat };
        },
        render() {
            return h('div', [
                h(
                    'button',
                    { id: 'declencheur', onClick: () => (this.etat.ouvert = true) },
                    'Ouvrir'
                ),
                h('button', { id: 'derriere' }, 'Élément de la page'),
                this.etat.ouvert ? h(Modale) : null,
            ]);
        },
    });

    return { Hote, etat };
}

function tabuler(shift = false) {
    document.dispatchEvent(
        new KeyboardEvent('keydown', {
            key: 'Tab',
            shiftKey: shift,
            bubbles: true,
            cancelable: true,
        })
    );
}

async function ouvrir(reglages = {}) {
    const { Hote, etat } = creerHote(reglages);
    const wrapper = mount(Hote, { attachTo: document.body });
    const declencheur = wrapper.find('#declencheur').element;

    /* Reproduit le clic réel : le bouton cliqué reçoit le focus. */
    declencheur.focus();
    await wrapper.find('#declencheur').trigger('click');
    await flushPromises();

    return { wrapper, declencheur, etat };
}

function element(wrapper, id) {
    return wrapper.find(`#${id}`).element;
}

async function fermer(etat) {
    etat.ouvert = false;
    await nextTick();
    await flushPromises();
}

describe('useFocusTrap', () => {
    it('place le focus sur le premier élément focusable par défaut', async () => {
        const { wrapper } = await ouvrir();

        expect(document.activeElement).toBe(element(wrapper, 'premier'));
    });

    it('focusInitial "conteneur" porte le focus sur la boîte entière', async () => {
        const { wrapper } = await ouvrir({ focusInitial: 'conteneur' });

        expect(document.activeElement).toBe(wrapper.find('.modal').element);
    });

    it('avance le focus dans l\'ordre du DOM', async () => {
        const { wrapper } = await ouvrir();

        element(wrapper, 'premier').focus();
        tabuler();

        expect(document.activeElement).toBe(element(wrapper, 'milieu'));
    });

    it('boucle du dernier élément au premier', async () => {
        const { wrapper } = await ouvrir();

        element(wrapper, 'dernier').focus();
        tabuler();

        expect(document.activeElement).toBe(element(wrapper, 'premier'));
    });

    it('boucle en sens inverse avec Maj + Tab', async () => {
        const { wrapper } = await ouvrir();

        element(wrapper, 'premier').focus();
        tabuler(true);

        expect(document.activeElement).toBe(element(wrapper, 'dernier'));
    });

    it('ramène le focus dans la modale quand il en est sorti', async () => {
        const { wrapper } = await ouvrir();

        element(wrapper, 'derriere').focus();
        tabuler();

        expect(document.activeElement).toBe(element(wrapper, 'premier'));

        element(wrapper, 'derriere').focus();
        tabuler(true);

        expect(document.activeElement).toBe(element(wrapper, 'dernier'));
    });

    it('ne laisse jamais filer le focus vers la page placée derrière', async () => {
        const { wrapper } = await ouvrir();

        for (let i = 0; i < 8; i += 1) {
            tabuler();
        }

        expect(wrapper.find('.modal').element.contains(document.activeElement)).toBe(true);
    });

    it('ignore les éléments désactivés et masqués', async () => {
        const { wrapper } = await ouvrir({ desactive: true, masque: true });

        element(wrapper, 'premier').focus();
        tabuler();

        /* Ni le bouton désactivé ni le bouton masqué ne sont atteints. */
        expect(document.activeElement).toBe(element(wrapper, 'milieu'));
    });

    it('neutralise Tab sans lever d\'erreur quand rien n\'est focusable', async () => {
        const { wrapper } = await ouvrir({ vide: true, desactive: true, masque: true });

        expect(document.activeElement).toBe(wrapper.find('.modal').element);
        expect(() => tabuler()).not.toThrow();
        expect(document.activeElement).toBe(wrapper.find('.modal').element);
    });

    it('recalcule la liste des éléments à chaque tabulation', async () => {
        const { wrapper, etat } = await ouvrir();

        element(wrapper, 'dernier').focus();
        tabuler();

        expect(document.activeElement).toBe(element(wrapper, 'premier'));

        /*
         * Un élément apparaît après l'ouverture : le cycle doit en tenir
         * compte sans qu'il faille rouvrir la modale.
         */
        etat.supplement = true;
        await nextTick();

        element(wrapper, 'dernier').focus();
        tabuler();

        expect(document.activeElement).toBe(element(wrapper, 'supplement'));
    });

    it('rend le focus au déclencheur à la fermeture', async () => {
        const { wrapper, declencheur, etat } = await ouvrir();

        element(wrapper, 'milieu').focus();
        await fermer(etat);

        expect(wrapper.find('.modal').exists()).toBe(false);
        expect(document.activeElement).toBe(declencheur);
    });

    it('ne focalise pas un déclencheur détaché du document', async () => {
        const { wrapper, etat } = await ouvrir();

        wrapper.find('#declencheur').element.remove();
        await fermer(etat);

        expect(wrapper.find('.modal').exists()).toBe(false);
        expect(document.activeElement).not.toBe(null);
    });

    it('laisse Échap se propager vers les gestionnaires de la modale', async () => {
        const { etat } = await ouvrir();

        let echapRecu = 0;
        const surTouche = event => {
            if (event.key === 'Escape') {
                echapRecu += 1;
            }
        };

        document.addEventListener('keydown', surTouche);

        const event = new KeyboardEvent('keydown', {
            key: 'Escape',
            bubbles: true,
            cancelable: true,
        });

        document.dispatchEvent(event);
        await flushPromises();

        /*
         * Le piège n'intercepte que `Tab` : la touche Échap continue de
         * circuler, ni neutralisée ni marquée comme traitée.
         */
        expect(echapRecu).toBe(1);
        expect(event.defaultPrevented).toBe(false);

        document.removeEventListener('keydown', surTouche);
        await fermer(etat);
    });
});
