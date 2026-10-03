import { onBeforeUnmount, watch } from 'vue';

// Pile des pièges actifs, du plus ancien au plus récent.
const pile = [];

/**
 * Piège de focus partagé pour les modales.
 *
 * Le composable n'intercepte que la touche `Tab` : `Escape` et les autres
 * raccourcis continuent de se propager pour laisser chaque modale appliquer
 * ses propres règles métier.
 *
 * @param {import('vue').Ref<HTMLElement|null>} element Modale à piéger.
 * @param {{ focusInitial?: 'premier'|'conteneur' }} options
 */
export function useFocusTrap(element, options = {}) {
    const { focusInitial = 'premier' } = options;

    let elementPrecedent = null;
    let actif = false;

    function estFocusable(candidat) {
        if (candidat.disabled || candidat.getAttribute('tabindex') === '-1') {
            return false;
        }

        if (candidat.tagName === 'INPUT' && candidat.type === 'hidden') {
            return false;
        }

        if (candidat.closest("[hidden], [aria-hidden='true'], [inert]")) {
            return false;
        }

        return typeof candidat.focus === 'function';
    }

    function elementsFocusables() {
        if (!element.value) {
            return [];
        }

        const selecteur = [
            'a[href]', 'button', 'input', 'select', 'textarea',
            'iframe', 'summary', '[contenteditable]', '[tabindex]',
        ].join(', ');

        return Array.from(element.value.querySelectorAll(selecteur)).filter(estFocusable);
    }

    function placerFocusInitial(conteneur) {
        if (focusInitial === 'conteneur') {
            conteneur.focus();
            return;
        }

        const premier = elementsFocusables()[0];
        (premier || conteneur).focus();
    }

    function surTouche(event) {
        if (event.key !== 'Tab' || !actif) {
            return;
        }

        // Seul le piège du sommet piège : deux modales ouvertes ne peuvent
        // pas se disputer la même touche.
        if (pile[pile.length - 1] !== piege) {
            return;
        }

        const focusables = elementsFocusables();

        if (focusables.length === 0) {
            event.preventDefault();
            return;
        }

        const index = focusables.indexOf(document.activeElement);

        let cible;

        if (event.shiftKey) {
            cible = index <= 0
                ? focusables[focusables.length - 1]
                : focusables[index - 1];
        } else {
            cible = index === -1 || index === focusables.length - 1
                ? focusables[0]
                : focusables[index + 1];
        }

        // Le cycle est toujours explicite : sans cela le navigateur
        // repartirait sur les éléments de la page situés derrière la modale.
        event.preventDefault();
        cible.focus();
    }

    const piege = { element };

    function activer(conteneur) {
        if (actif || !conteneur) {
            return;
        }

        actif = true;
        elementPrecedent = document.activeElement;
        pile.push(piege);
        document.addEventListener('keydown', surTouche);
        placerFocusInitial(conteneur);
    }

    function desactiver() {
        if (!actif) {
            return;
        }

        actif = false;
        document.removeEventListener('keydown', surTouche);

        const position = pile.indexOf(piege);

        if (position !== -1) {
            pile.splice(position, 1);
        }

        const cible = elementPrecedent;
        elementPrecedent = null;

        /*
         * La restitution évite que la disparition de la modale ne renvoie
         * l'utilisateur sur `body`. Le contrôle `document.contains` évite
         * de focaliser un déclencheur détaché, par exemple si la liste a
         * été rechargée pendant l'ouverture.
         */
        if (
            cible &&
            cible !== document.body &&
            document.contains(cible) &&
            typeof cible.focus === 'function'
        ) {
            cible.focus();
        }
    }

    // La modale étant rendue sous `v-if`, sa référence n'arrive qu'à
    // l'ouverture : c'est ce changement qui arme et désarme le piège.
    watch(element, conteneur => (conteneur ? activer(conteneur) : desactiver()), {
        immediate: true,
        flush: 'post',
    });

    onBeforeUnmount(desactiver);

    return { elementsFocusables };
}
