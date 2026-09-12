import api from "./api";

/**
 * Récupère les équipements du parc.
 */
export async function getEquipementsDashboard() {
    const response = await api.get("/inventaire/equipements/");
    return response.data;
}

/**
 * Récupère les bâtiments.
 */
export async function getBatimentsDashboard() {
    const response = await api.get("/inventaire/batiments/");
    return response.data;
}

/**
 * Récupère les étages.
 */
export async function getEtagesDashboard() {
    const response = await api.get("/inventaire/etages/");
    return response.data;
}

/**
 * Récupère les salles.
 */
export async function getSallesDashboard() {
    const response = await api.get("/inventaire/salles/");
    return response.data;
}

/**
 * Récupère les rapports d'audit.
 */
export async function getRapportsAuditDashboard() {
    const response = await api.get("/audit/rapports/");
    return response.data;
}