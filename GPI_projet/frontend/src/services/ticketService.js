import api from "./api";

/**
 * Récupère tous les tickets.
 */
export async function getTickets() {
    const response = await api.get(
        "/inventaire/tickets-panne/"
    );

    return response.data;
}

/**
 * Récupère un ticket précis.
 */
export async function getTicket(ticketId) {
    const response = await api.get(
        `/inventaire/tickets-panne/${ticketId}/`
    );

    return response.data;
}

/**
 * Crée un nouveau ticket.
 */
export async function creerTicket(
    equipementId,
    titre,
    description,
    type = "MAINTENANCE",
    priorite = "NORMALE"
) {
    const response = await api.post(
        "/inventaire/tickets-panne/",
        {
            equipement: equipementId,
            titre,
            description,
            type,
            priorite,
        }
    );

    return response.data;
}

export async function prendreEnChargeTicket(ticketId) {
    const response = await api.post(
        `/inventaire/tickets-panne/${ticketId}/prendre-en-charge/`
    );

    return response.data;
}

/**
 * Résout un ticket.
 */
export async function resoudreTicket(ticketId, commentaireResolution) {
    const response = await api.post(
        `/inventaire/tickets-panne/${ticketId}/resoudre/`,
        {
            commentaire_resolution: commentaireResolution,
        }
    );

    return response.data;
}