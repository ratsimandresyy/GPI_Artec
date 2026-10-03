import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { nextTick } from 'vue';

import PlanViewer from '../PlanViewer.vue';
import { deplacerEquipement as sauvegarderDeplacement } from '../../services/localisationService';
import { getEquipementsDashboard } from '../../services/dashboardService';
import { getSalles } from '../../services/salleService';

/*
 * Non-régression de l'accessibilité clavier des marqueurs du plan.
 *
 * Ces tests protègent trois exigences :
 *   - le marqueur est atteignable et activable au clavier ;
 *   - clic, Entrée et Espace appellent la même fonction ;
 *   - le glisser à la souris, ses coordonnées comprises, n'est ni
 *     modifié ni déclenché par une pression clavier.
 */

vi.mock('../../services/localisationService', () => ({
    deplacerEquipement: vi.fn(),
    getPositionsParPlan: vi.fn(),
}));

vi.mock('../../services/dashboardService', () => ({
    getEquipementsDashboard: vi.fn(),
}));

vi.mock('../../services/salleService', () => ({
    getSalles: vi.fn(),
}));

vi.mock('../../services/stockService', () => ({
    transfererVersStock: vi.fn(),
    affecterEquipement: vi.fn(),
}));

const PLAN = {
    id: 1,
    nom: "RDC",
    largeur: 1000,
    hauteur: 800,
};

const EQUIPEMENT = {
    id: 10,
    nom: "Vidéoprojecteur",
    numero_inventaire: "INV-010",
    etat: "EN_SERVICE",
};

/*
 * Le composant travaille sur les objets reçus en props et déplace
 * leurs coordonnées en place : chaque test reçoit donc une position
 * neuve, sinon un test de glisser contaminerait le suivant.
 */
function positionInitiale() {
    return {
        id: 100,
        plan: 1,
        equipement: 10,
        equipement_nom: "Vidéoprojecteur",
        x: 120,
        y: 240,
    };
}

async function monter(estAdmin = false, { attache = false } = {}) {
    const wrapper = mount(PlanViewer, {
        props: {
            plan: { ...PLAN },
            positions: [positionInitiale()],
            equipements: [{ ...EQUIPEMENT }],
            estAdmin,
        },
        global: {
            stubs: { RouterLink: true },
        },
        attachTo: attache ? document.body : undefined,
    });

    await flushPromises();

    return wrapper;
}

/* Dépôt d'un équipement du stock sur le plan, à la souris. */
async function deposerSurPlan(wrapper, equipementId) {
    const evenement = new Event('drop', { bubbles: true, cancelable: true });

    /* jsdom ne fournit pas de dataTransfer : on en fabrique un minimal. */
    Object.defineProperty(evenement, 'dataTransfer', {
        value: {
            getData: () => JSON.stringify({ equipementId }),
            setData: vi.fn(),
        },
    });

    wrapper.find('.plan-wrapper').element.dispatchEvent(evenement);

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

/* Premier marqueur rendu sur le plan. */
function marqueur(wrapper) {
    return wrapper.find('.equipement-marker');
}

describe("PlanViewer.vue — marqueurs d'équipement", () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.spyOn(console, 'error').mockImplementation(() => {});

        getEquipementsDashboard.mockResolvedValue([]);
        getSalles.mockResolvedValue([]);
        sauvegarderDeplacement.mockResolvedValue({});
    });

    it("expose le marqueur comme un bouton atteignable au clavier", async () => {
        const wrapper = await monter();
        const element = marqueur(wrapper);

        expect(element.exists()).toBe(true);
        expect(element.attributes('role')).toBe('button');
        expect(element.attributes('tabindex')).toBe('0');

        /*
         * Le nom accessible reprend exactement l'infobulle déjà
         * affichée au survol, elle-même tirée du nom et de l'état
         * visibles sur le marqueur.
         */
        expect(element.attributes('aria-label')).toBe(
            element.attributes('title')
        );
        expect(element.attributes('aria-label')).toContain('Vidéoprojecteur');
    });

    it("déclenche la même action au clic et à la touche Entrée", async () => {
        const wrapper = await monter();

        await marqueur(wrapper).trigger('click');
        const auClic = wrapper.emitted('equipement-clic');

        expect(auClic).toHaveLength(1);
        expect(auClic[0][0]).toEqual(EQUIPEMENT);

        await marqueur(wrapper).trigger('keydown.enter');
        const emissions = wrapper.emitted('equipement-clic');

        expect(emissions).toHaveLength(2);
        expect(emissions[1]).toEqual(auClic[0]);
    });

    it("déclenche la même action à la touche Espace et neutralise le défilement", async () => {
        const wrapper = await monter();

        const evenement = new KeyboardEvent("keydown", {
            key: " ",
            bubbles: true,
            cancelable: true,
        });

        marqueur(wrapper).element.dispatchEvent(evenement);
        await nextTick();

        expect(wrapper.emitted('equipement-clic')).toHaveLength(1);
        expect(wrapper.emitted('equipement-clic')[0][0]).toEqual(EQUIPEMENT);

        /* Sans .prevent, Espace ferait défiler la page. */
        expect(evenement.defaultPrevented).toBe(true);
    });

    it("conserve le glisser à la souris et ses coordonnées", async () => {
        const wrapper = await monter(true);

        expect(
            marqueur(wrapper).attributes('style')
        ).toContain('left: 120px');

        await marqueur(wrapper).trigger('mousedown');

        /* jsdom renvoie un rectangule à zéro : le décalage est nul. */
        wrapper.find('.plan-wrapper').element.dispatchEvent(
            new MouseEvent("mousemove", {
                bubbles: true,
                clientX: 300,
                clientY: 400,
            })
        );

        await nextTick();

        const style = marqueur(wrapper).attributes('style');

        expect(style).toContain('left: 300px');
        expect(style).toContain('top: 400px');
    });

    it("ne déplace jamais un marqueur à la suite d'une pression clavier", async () => {
        const wrapper = await monter(true);

        await marqueur(wrapper).trigger('keydown.enter');
        await marqueur(wrapper).trigger('keydown.space');
        await nextTick();

        /* Aucune coordonnée ne doit bouger : le glisser reste lié à la souris. */
        const style = marqueur(wrapper).attributes('style');

        expect(style).toContain('left: 120px');
        expect(style).toContain('top: 240px');
        expect(sauvegarderDeplacement).not.toHaveBeenCalled();
    });

    it("emprisonne le focus dans la modale d'affectation", async () => {
        getEquipementsDashboard.mockResolvedValue([
            {
                id: 55,
                nom: 'Projecteur de réserve',
                numero_inventaire: 'INV-055',
                etat: 'EN_SERVICE',
                situation: 'EN_STOCK',
            },
        ]);

        const wrapper = await monter(true, { attache: true });

        await deposerSurPlan(wrapper, 55);

        const modale = wrapper.find('[role="dialog"]');

        expect(modale.exists()).toBe(true);

        /* Le focus entre dans la modale ouverte depuis le plan. */
        expect(document.activeElement).toBe(modale.element);

        for (let i = 0; i < 8; i += 1) {
            tabuler();
        }

        expect(modale.element.contains(document.activeElement)).toBe(true);

        /* Échap referme toujours la modale. */
        document.dispatchEvent(
            new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })
        );
        await nextTick();

        expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
    });
});
