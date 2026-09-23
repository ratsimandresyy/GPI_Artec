import api from "./api";

/**
 * Récupère tous les rapports d'audit.
 */
export async function getRapportsAudit() {
    const response = await api.get("/audit/rapports/");
    return response.data;
}

/**
 * Récupère un rapport d'audit précis.
 */
export async function getRapportAudit(id) {
    const response = await api.get(`/audit/rapports/${id}/`);
    return response.data;
}

/**
 * Récupère toutes les connexions issues des audits.
 */
export async function getConnexionsAudit() {
    const response = await api.get("/audit/connexions/");
    return response.data;
}