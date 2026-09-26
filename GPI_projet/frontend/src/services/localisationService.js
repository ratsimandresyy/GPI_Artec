import api from "./api";

/**
 * Récupère tous les plans.
 */
export async function getPlans() {
    const response = await api.get(
        "/inventaire/plans/"
    );

    return response.data;
}

/**
 * Récupère toutes les positions.
 */
export async function getPositions() {
    const response = await api.get(
        "/inventaire/positions/"
    );

    return response.data;
}

/**
 * Récupère les positions associées à un plan.
 *
 * Le backend retourne actuellement toutes les positions.
 * Le filtrage est donc effectué côté frontend.
 *
 * @param {number} planId
 */
export async function getPositionsParPlan(planId) {
    const positions = await getPositions();

    return positions.filter(
        (position) =>
            String(position.plan) ===
            String(planId)
    );
}

/**
 * Localise un équipement.
 *
 * @param {number} equipementId
 * @param {number} planId
 * @param {number} x
 * @param {number} y
 */
export async function localiserEquipement(
    equipementId,
    planId,
    x,
    y
) {
    const response = await api.post(
        "/inventaire/positions/localiser/",
        {
            equipement: equipementId,
            plan: planId,
            x,
            y,
        }
    );

    return response.data;
}

/**
 * Déplace un équipement déjà localisé.
 *
 * @param {number} positionId
 * @param {number} planId
 * @param {number} x
 * @param {number} y
 */
export async function deplacerEquipement(
    positionId,
    planId,
    x,
    y
) {
    const response = await api.post(
        `/inventaire/positions/${positionId}/deplacer/`,
        {
            plan: planId,
            x,
            y,
        }
    );

    return response.data;
}

/**
 * Supprime la localisation d'un équipement.
 *
 * @param {number} positionId
 */
export async function supprimerLocalisation(
    positionId
) {
    await api.delete(
        `/inventaire/positions/${positionId}/`
    );
}