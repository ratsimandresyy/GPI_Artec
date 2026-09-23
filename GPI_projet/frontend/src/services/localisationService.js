import api from "./api";


// Récupérer tous les plans
export async function getPlans() {
    const response = await api.get(
        "/inventaire/plans/"
    );

    return response.data;
}


// Récupérer toutes les positions
export async function getPositions() {
    const response = await api.get(
        "/inventaire/positions/"
    );

    return response.data;
}


// Récupérer les positions d'un plan
export async function getPositionsParPlan(planId) {

    const positions = await getPositions();

    return positions.filter(
        (position) =>
            String(position.plan) === String(planId)
    );
}


// Modifier la position d'un équipement
export async function modifierPosition(
    id,
    donnees
) {
    const response = await api.put(
        `/inventaire/positions/${id}/`,
        donnees
    );

    return response.data;
}