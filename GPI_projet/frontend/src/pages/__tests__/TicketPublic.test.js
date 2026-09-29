import { beforeEach, describe, expect, it, vi } from 'vitest';
import { flushPromises, mount } from '@vue/test-utils';
import { createPinia, setActivePinia } from 'pinia';

import TicketPublic from '../TicketPublic.vue';
import { creerTicket } from '../../services/ticketService';
import { getEquipementsDashboard } from '../../services/dashboardService';
import { useNotificationStore } from '../../stores/notifications';

vi.mock('../../services/ticketService', () => ({
    creerTicket: vi.fn(),
}));

vi.mock('../../services/dashboardService', () => ({
    getEquipementsDashboard: vi.fn(),
}));

/*
 * Les valeurs de situation et d'état reprennent celles du modèle Django
 * (voir backend/inventaire/models/equipement.py) : AFFECTE / EN_STOCK et
 * EN_SERVICE / EN_PANNE / EN_MAINTENANCE.
 */

/** Équipement proposable au signalement : affecté, et non en panne. */
function equipementValide(id, nom, numeroInventaire, etat = 'EN_SERVICE') {
    return {
        id,
        nom,
        numero_inventaire: numeroInventaire,
        situation: 'AFFECTE',
        etat,
    };
}

/** Promesse qui ne se résout jamais : simule un chargement en cours. */
function jamaisResolu() {
    return new Promise(() => {});
}

/** Monte le composant avec un Pinia isolé et les notifications spyées. */
async function monter() {
    const pinia = createPinia();
    setActivePinia(pinia);

    const store = useNotificationStore();
    const success = vi.spyOn(store, 'success').mockReturnValue(1);
    const erreur = vi.spyOn(store, 'error').mockReturnValue(2);

    const wrapper = mount(TicketPublic, {
        global: { plugins: [pinia] },
    });

    await flushPromises();

    return { wrapper, success, erreur };
}

/** Ids référencés par aria-describedby sur le sélecteur d'équipement. */
function idsDecrits(wrapper) {
    const describedBy = wrapper
        .find('#equipement')
        .attributes('aria-describedby');

    return (describedBy || '').split(/\s+/).filter(Boolean);
}

/**
 * Invariant réutilisable sur les trois états du sélecteur : chaque id
 * annoncé par aria-describedby doit exister, et aucun id ne doit être
 * dupliqué dans le composant monté.
 */
function verifierAriaDecrits(wrapper) {
    for (const id of idsDecrits(wrapper)) {
        expect(
            wrapper.find(`#${id}`).exists(),
            `aria-describedby pointe vers un id absent : ${id}`
        ).toBe(true);
    }

    const ids = wrapper.findAll('[id]').map((el) => el.attributes('id'));

    expect(
        ids.length,
        `id dupliqué(s) : ${ids.filter((id, i) => ids.indexOf(id) !== i).join(', ')}`
    ).toBe(new Set(ids).size);
}

/** Remplit les champs obligatoires avec un équipement disponible. */
async function remplirFormulaireValide(wrapper) {
    await wrapper.find('#equipement').setValue('1');
    await wrapper.find('#titre').setValue('  Écran noir au démarrage  ');
    await wrapper.find('#description').setValue(
        "  L'écran reste noir après démarrage.  "
    );
}

describe('TicketPublic.vue', () => {
    beforeEach(() => {
        vi.clearAllMocks();

        // Le composant journalise les erreurs attendues : on évite de
        // polluer la sortie de `npm test` sans masquer de vrai défaut.
        vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    describe('selecteur d\'équipement', () => {
        it('affiche un état de chargement explicite', async () => {
            getEquipementsDashboard.mockReturnValue(jamaisResolu());

            const { wrapper } = await monter();

            const select = wrapper.find('#equipement');

            expect(select.exists()).toBe(true);
            expect(select.attributes('disabled')).toBeDefined();
            expect(select.find('option').text()).toBe(
                'Chargement des équipements…'
            );
            expect(idsDecrits(wrapper)).toEqual([
                'equipement-aide-salle-requise',
            ]);
            expect(
                wrapper.find('#equipement-aide-salle-requise').exists()
            ).toBe(true);
            expect(
                wrapper.find('#equipement-aide-indisponible').exists()
            ).toBe(false);

            verifierAriaDecrits(wrapper);
        });

        it('bascule vers l\'aide « aucun équipement » quand la liste est vide', async () => {
            getEquipementsDashboard.mockResolvedValue([]);

            const { wrapper } = await monter();

            expect(idsDecrits(wrapper)).toEqual([
                'equipement-aide-indisponible',
            ]);
            expect(wrapper.find('#equipement-aide-indisponible').text()).toContain(
                "Aucun équipement affecté n'est disponible pour le signalement."
            );
            expect(
                wrapper.find('#equipement-aide-salle-requise').exists()
            ).toBe(false);

            verifierAriaDecrits(wrapper);
        });

        it('affiche l\'aide « salle requise » quand un équipement est disponible', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);

            const { wrapper } = await monter();

            expect(idsDecrits(wrapper)).toEqual([
                'equipement-aide-salle-requise',
            ]);
            expect(
                wrapper.find('#equipement-aide-salle-requise').text()
            ).toContain(
                "Seuls les équipements affectés à une salle peuvent être signalés."
            );
            expect(
                wrapper.find('#equipement-aide-indisponible').exists()
            ).toBe(false);

            verifierAriaDecrits(wrapper);
        });

        it('relie aria-describedby à un id existant et n\'utilise aucun id dupliqué, quel que soit l\'état', async () => {
            const etats = [
                {
                    nom: 'chargement en cours',
                    retour: jamaisResolu(),
                },
                {
                    nom: 'aucun équipement disponible',
                    retour: [],
                },
                {
                    nom: 'équipements disponibles',
                    retour: [
                        equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
                        equipementValide(2, 'Imprimante', 'INV-002'),
                    ],
                },
            ];

            for (const etat of etats) {
                getEquipementsDashboard.mockReturnValue(etat.retour);

                const { wrapper } = await monter();

                expect(
                    idsDecrits(wrapper).length,
                    `${etat.nom} : aria-describedby est vide`
                ).toBeGreaterThan(0);

                verifierAriaDecrits(wrapper);

                wrapper.unmount();
            }
        });

        it('propose uniquement les équipements affectés et non en panne', async () => {
            getEquipementsDashboard.mockResolvedValue([
                // Non affecté : jamais signalable depuis cette interface.
                {
                    ...equipementValide(1, 'Ordinateur', 'INV-001'),
                    situation: 'EN_STOCK',
                },
                // Déjà en panne : l'API refuserait la création.
                {
                    ...equipementValide(2, 'Vidéoprojecteur', 'INV-002'),
                    etat: 'EN_PANNE',
                },
                equipementValide(3, 'Imprimante', 'INV-003', 'EN_SERVICE'),
                // Seul EN_PANNE est filtré : EN_MAINTENANCE reste proposé.
                equipementValide(4, 'Écran', 'INV-004', 'EN_MAINTENANCE'),
            ]);

            const { wrapper } = await monter();

            const options = wrapper.findAll('#equipement option');

            // 1 option vide + 2 équipements affectés et non en panne.
            expect(options).toHaveLength(3);
            expect(options[1].text()).toContain('Imprimante');
            expect(options[1].text()).toContain('INV-003');
            expect(options[2].text()).toContain('Écran');
            expect(options[2].text()).toContain('INV-004');

            // Ni l'équipement en stock ni celui déjà en panne ne sont proposés.
            expect(wrapper.text()).not.toContain('Ordinateur');
            expect(wrapper.text()).not.toContain('Vidéoprojecteur');
        });

        it('retombe sur l\'état vide si tous les équipements sont filtrés', async () => {
            getEquipementsDashboard.mockResolvedValue([
                {
                    ...equipementValide(1, 'Ordinateur', 'INV-001'),
                    situation: 'EN_STOCK',
                },
                {
                    ...equipementValide(2, 'Imprimante', 'INV-002'),
                    situation: 'EN_STOCK',
                },
                {
                    ...equipementValide(3, 'Écran', 'INV-003'),
                    etat: 'EN_PANNE',
                },
            ]);

            const { wrapper } = await monter();

            expect(idsDecrits(wrapper)).toEqual([
                'equipement-aide-indisponible',
            ]);
            expect(
                wrapper.find('#equipement-aide-indisponible').exists()
            ).toBe(true);
            expect(
                wrapper.find('#equipement-aide-salle-requise').exists()
            ).toBe(false);
            expect(wrapper.findAll('#equipement option')).toHaveLength(1);
        });
    });

    describe('chargement des équipements', () => {
        it('affiche une alerte et masque le formulaire si le chargement échoue', async () => {
            getEquipementsDashboard.mockRejectedValue(
                new Error('réseau indisponible')
            );

            const { wrapper } = await monter();

            const alerte = wrapper.find('[role="alert"]');

            expect(alerte.exists()).toBe(true);
            expect(alerte.text()).toContain(
                'Impossible de charger la liste des équipements'
            );
            expect(wrapper.find('form').exists()).toBe(false);
            expect(wrapper.find('#equipement').exists()).toBe(false);
        });
    });

    describe('validation et soumission', () => {
        it('refuse l\'envoi sans équipement sélectionné', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockResolvedValue({ id: 1 });

            const { wrapper } = await monter();

            await wrapper.find('#titre').setValue('Écran noir');
            await wrapper
                .find('#description')
                .setValue("L'écran ne s'allume plus.");
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(creerTicket).not.toHaveBeenCalled();
            expect(wrapper.find('[role="alert"]').text()).toContain(
                'Veuillez sélectionner un équipement.'
            );
        });

        it('affiche une erreur sous le titre lorsqu\'il est vide', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockResolvedValue({ id: 1 });

            const { wrapper } = await monter();

            await wrapper.find('#equipement').setValue('1');
            await wrapper
                .find('#description')
                .setValue("L'écran ne s'allume plus.");
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(creerTicket).not.toHaveBeenCalled();
            expect(wrapper.find('#erreur-titre').text()).toBe(
                'Veuillez saisir un titre.'
            );
        });

        it('affiche une erreur sous la description lorsqu\'elle est vide', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockResolvedValue({ id: 1 });

            const { wrapper } = await monter();

            await wrapper.find('#equipement').setValue('1');
            await wrapper.find('#titre').setValue('Écran noir');
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(creerTicket).not.toHaveBeenCalled();
            expect(wrapper.find('#erreur-description').text()).toBe(
                'Veuillez décrire le problème rencontré.'
            );
        });

        it('envoie un signalement valide puis réinitialise le formulaire', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockResolvedValue({ id: 7 });

            const { wrapper, success } = await monter();

            await remplirFormulaireValide(wrapper);
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(creerTicket).toHaveBeenCalledTimes(1);
            // v-model restitue la valeur brute liée à l'option : l'identifiant
            // reste numérique, comme attendu par l'API.
            expect(creerTicket).toHaveBeenCalledWith(
                1,
                'Écran noir au démarrage',
                "L'écran reste noir après démarrage.",
                'MAINTENANCE',
                'NORMALE'
            );
            expect(success).toHaveBeenCalledWith(
                "Signalement envoyé à l'équipe technique."
            );

            expect(wrapper.find('#equipement').element.value).toBe('');
            expect(wrapper.find('#titre').element.value).toBe('');
            expect(wrapper.find('#description').element.value).toBe('');

            expect(wrapper.find('[role="status"]').text()).toContain(
                'Signalement envoyé.'
            );
            expect(
                wrapper.find('button.btn-secondary').text()
            ).toContain('Nouveau signalement');
        });

        it('affiche le détail renvoyé par l\'API quand l\'envoi échoue', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockRejectedValue({
                response: { data: { detail: 'Cet équipement est déjà en panne.' } },
            });

            const { wrapper, erreur } = await monter();

            await remplirFormulaireValide(wrapper);
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(wrapper.find('[role="alert"]').text()).toContain(
                'Cet équipement est déjà en panne.'
            );
            expect(erreur).toHaveBeenCalledWith(
                'Cet équipement est déjà en panne.'
            );

            // Le formulaire redevient utilisable après l'échec.
            expect(
                wrapper.find('button[type="submit"]').attributes('disabled')
            ).toBeUndefined();
        });
    });

    describe('références ARIA conditionnelles', () => {
        it('n\'annonce aucun message d\'erreur quand le formulaire est valide', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);

            const { wrapper } = await monter();

            // Sans erreur, aria-describedby doit être absent : l'attribut
            // ne doit pointer vers aucun id.
            expect(
                wrapper.find('#titre').attributes('aria-describedby')
            ).toBeUndefined();
            expect(
                wrapper.find('#description').attributes('aria-describedby')
            ).toBeUndefined();
        });

        it('lie aria-describedby au message d\'erreur dès qu\'il apparaît', async () => {
            getEquipementsDashboard.mockResolvedValue([
                equipementValide(1, 'Vidéoprojecteur', 'INV-001'),
            ]);
            creerTicket.mockResolvedValue({ id: 1 });

            const { wrapper } = await monter();

            await wrapper.find('#equipement').setValue('1');
            await wrapper
                .find('#description')
                .setValue("L'écran ne s'allume plus.");
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(wrapper.find('#titre').attributes('aria-describedby')).toBe(
                'erreur-titre'
            );
            expect(wrapper.find('#erreur-titre').exists()).toBe(true);
            expect(
                wrapper.find('#titre').attributes('aria-invalid')
            ).toBe('true');

            // La description est renseignée : aucune référence émise.
            expect(
                wrapper.find('#description').attributes('aria-describedby')
            ).toBeUndefined();

            await wrapper.find('#titre').setValue('Écran noir');
            await wrapper.find('#description').setValue('');
            await wrapper.find('form').trigger('submit');
            await flushPromises();

            expect(
                wrapper.find('#description').attributes('aria-describedby')
            ).toBe('erreur-description');
            expect(wrapper.find('#erreur-description').exists()).toBe(true);
            expect(
                wrapper.find('#description').attributes('aria-invalid')
            ).toBe('true');

            // L'erreur du titre est levée : sa référence disparaît aussi.
            expect(wrapper.find('#erreur-titre').exists()).toBe(false);
            expect(
                wrapper.find('#titre').attributes('aria-describedby')
            ).toBeUndefined();
            expect(wrapper.find('#titre').attributes('aria-invalid')).toBe(
                'false'
            );
        });
    });
});
