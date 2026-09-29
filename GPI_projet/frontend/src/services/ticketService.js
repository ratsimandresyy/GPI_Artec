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
 *
 * `etatFinal` traduit le diagnostic de fin d'intervention
 * (diagramme d'activité « Matériel réparé ? ») : "EN_SERVICE" si le
 * matériel est remis en service, "HORS_SERVICE" sinon.
 */
export async function resoudreTicket(
    ticketId,
    commentaireResolution,
    etatFinal = "EN_SERVICE"
) {
    const response = await api.post(
        `/inventaire/tickets-panne/${ticketId}/resoudre/`,
        {
            commentaire_resolution: commentaireResolution,
            etat_final: etatFinal,
        }
    );

    return response.data;
}

/**
 * Qualifie un ticket : type et/ou priorité.
 *
 * Diagramme d'activité « Qualifier le ticket : définir le type,
 * définir la priorité ». Les valeurs non fournies restent inchangées.
 */
export async function qualifierTicket(
    ticketId,
    { type = null, priorite = null } = {}
) {
    const response = await api.post(
        `/inventaire/tickets-panne/${ticketId}/qualifier/`,
        {
            type,
            priorite,
        }
    );

    return response.data;
}