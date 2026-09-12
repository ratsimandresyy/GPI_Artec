import api from "./api";

/**
 * Récupère la liste des bâtiments.
 */
export async function getBatiments() {
    const response = await api.get("/inventaire/batiments/");
    return response.data;
}

/**
 * Récupère un bâtiment par son identifiant.
 */
export async function getBatiment(id) {
    const response = await api.get(
        `/inventaire/batiments/${id}/`
    );
    return response.data;
}

/**
 * Crée un nouveau bâtiment.
 */
export async function creerBatiment(donnees) {
    const response = await api.post(
        "/inventaire/batiments/",
        donnees
    );
    return response.data;
}

/**
 * Modifie un bâtiment existant.
 */
export async function modifierBatiment(id, donnees) {
    const response = await api.put(
        `/inventaire/batiments/${id}/`,
        donnees
    );
    return response.data;
}

/**
 * Supprime un bâtiment.
 */
export async function supprimerBatiment(id) {
    await api.delete(
        `/inventaire/batiments/${id}/`
    );
}