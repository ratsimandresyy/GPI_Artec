import api from "./api";

/**
 * Transfère un équipement affecté vers le stock.
 *
 * @param {number} equipementId
 * @param {string} conditionStock
 */
export async function transfererVersStock(
    equipementId,
    conditionStock
) {
    const response = await api.post(
        `/inventaire/equipements/${equipementId}/transferer-vers-stock/`,
        {
            condition_stock: conditionStock,
        }
    );

    return response.data;
}


/**
 * Termine la maintenance d'un équipement
 * actuellement en stock.
 *
 * @param {number} equipementId
 */
export async function terminerMaintenance(
    equipementId
) {
    const response = await api.post(
        `/inventaire/equipements/${equipementId}/terminer-maintenance/`
    );

    return response.data;
}


/**
 * Affecte un équipement du stock
 * à une salle et le localise sur un plan.
 *
 * @param {number} equipementId
 * @param {number} salleId
 * @param {number} planId
 * @param {number} x
 * @param {number} y
 */
export async function affecterEquipement(
    equipementId,
    salleId,
    planId,
    x,
    y
) {
    const response = await api.post(
        `/inventaire/equipements/${equipementId}/affecter/`,
        {
            salle: salleId,
            plan: planId,
            x,
            y,
        }
    );

    return response.data;
}
