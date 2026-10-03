import { afterEach, describe, expect, it, vi } from 'vitest';
import {
    enableAutoUnmount,
    flushPromises,
    mount,
} from '@vue/test-utils';
import { defineComponent, h, nextTick, ref } from 'vue';

import ConfirmDialog from '../ConfirmDialog.vue';

/*
 * Non-régression du cycle de vie clavier de la boîte de confirmation.
 *
 * Elle capte le focus à l'ouverture, le rend sur l'annulation, et le
 * restitue à la fermeture : sans cette restitution, la disparition de
 * la boîte renvoyait le focus sur `body` et l'utilisateur devait
 * retrouver seul son bouton déclencheur.
 *
 * Le montage est attaché au document : sans cela, aucun élément ne peut
 * réellement recevoir le focus et les assertions de focus seraient
 * toujours fausses.
 */

enableAutoUnmount(afterEach);

const PROPS = {
    titre: "Supprimer l'équipement",
    message: "L'équipement Vidéoprojecteur sera supprimé.",
};

/* Déclencheur + boîte conditionnelle, pour observer la restitution. */
const Hote = defineComponent({
    props: {
        danger: { type: Boolean, default: true },
    },
    setup(props) {
        const ouvert = ref(false);

        const fermer = () => {
            ouvert.value = false;
        };

        return { ouvert, fermer, props };
    },
    render() {
        return h('div', [
            h(
                'button',
                {
                    id: 'declencheur',
                    onClick: () => {
                        this.ouvert = true;
                    },
                },
                'Supprimer'
            ),

            this.ouvert
                ? h(ConfirmDialog, {
                      titre: PROPS.titre,
                      message: PROPS.message,
                      danger: this.props.danger,
                      onCancel: this.fermer,
                  })
                : null,
        ]);
    },
});

function monterBoite() {
    return mount(ConfirmDialog, {
        props: { ...PROPS },
        attachTo: document.body,
    });
}

async function appuiEchap() {
    document.dispatchEvent(
        new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
    );
    await nextTick();
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

describe('ConfirmDialog.vue — focus et clavier', () => {
    it('place le focus sur le bouton d\'annulation à l\'ouverture', async () => {
        const wrapper = monterBoite();

        await flushPromises();

        const annuler = wrapper
            .findAll('button')
            .find((b) => b.text() === 'Annuler');

        expect(document.activeElement).toBe(annuler.element);
    });

    it('ferme avec la touche Échap', async () => {
        const wrapper = monterBoite();

        await flushPromises();
        await appuiEchap();

        expect(wrapper.emitted('cancel')).toHaveLength(1);
    });

    it('rend le focus au bouton déclencheur à la fermeture', async () => {
        const wrapper = mount(Hote, { attachTo: document.body });

        const declencheur = wrapper.find('#declencheur');

        /*
         * Un clic réel dans un navigateur donne le focus au bouton
         * cliqué : `trigger` ne le fait pas, il faut le faire ici pour
         * reproduire fidèlement le comportement de l'utilisateur.
         */
        declencheur.element.focus();
        await declencheur.trigger('click');
        await flushPromises();

        /* Le focus est bien entré dans la boîte. */
        expect(document.activeElement).not.toBe(declencheur.element);

        /* Fermeture par Échap : la boîte disparaît. */
        await appuiEchap();
        await flushPromises();

        expect(wrapper.find('.confirm').exists()).toBe(false);
        expect(document.activeElement).toBe(declencheur.element);
    });

    it('ne focalise pas un élément détaché', async () => {
        const wrapper = mount(Hote, { attachTo: document.body });

        await wrapper.find('#declencheur').trigger('click');
        await flushPromises();

        /*
         * Le déclencheur disparaît du document avant la fermeture :
         * la restauration doit être ignorée, sans lever d'erreur.
         */
        wrapper.find('#declencheur').element.remove();

        await appuiEchap();
        await flushPromises();

        expect(wrapper.find('.confirm').exists()).toBe(false);
        expect(document.activeElement).not.toBe(null);
    });

    it('emprisonne le focus dans la boîte', async () => {
        const wrapper = monterBoite();

        await flushPromises();

        const annuler = wrapper
            .findAll('button')
            .find((b) => b.text() === 'Annuler');

        const supprimer = wrapper
            .findAll('button')
            .find((b) => b.text() === 'Supprimer');

        /* Tab passe de l'annulation à la confirmation. */
        tabuler();
        expect(document.activeElement).toBe(supprimer.element);

        /* Tab reboucle sur l'annulation : la page n'est jamais atteinte. */
        tabuler();
        expect(document.activeElement).toBe(annuler.element);

        /* Maj + Tab remonte de l'autre côté. */
        tabuler(true);
        expect(document.activeElement).toBe(supprimer.element);
    });

    it('expose des boutons natifs et des relations ARIA valides', async () => {
        const wrapper = monterBoite();

        await flushPromises();

        const boutons = wrapper.findAll('button');

        expect(boutons).toHaveLength(2);
        boutons.forEach((bouton) => {
            expect(bouton.attributes('type')).toBe('button');
            /* Nom accessible : le texte visible, jamais une icône seule. */
            expect(bouton.text().trim()).not.toBe('');
        });

        const boite = wrapper.find('[role="alertdialog"]');

        expect(boite.attributes('aria-modal')).toBe('true');

        const titreId = boite.attributes('aria-labelledby');
        const messageId = boite.attributes('aria-describedby');

        expect(wrapper.find(`#${titreId}`).exists()).toBe(true);
        expect(wrapper.find(`#${messageId}`).exists()).toBe(true);
    });
});
