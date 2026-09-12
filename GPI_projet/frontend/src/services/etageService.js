import api from "./api";


// Récupérer tous les étages
export async function getEtages() {
    const response = await api.get("/inventaire/etages/");
    return response.data;
}


// Récupérer un étage par son ID
export async function getEtage(id) {
    const response = await api.get(
        `/inventaire/etages/${id}/`
    );

    return response.data;
}


// Créer un étage
export async function creerEtage(donnees) {
    const response = await api.post(
        "/inventaire/etages/",
        donnees
    );

    return response.data;
}


// Modifier un étage
export async function modifierEtage(id, donnees) {
    const response = await api.put(
        `/inventaire/etages/${id}/`,
        donnees
    );

    return response.data;
}


// Supprimer un étage
export async function supprimerEtage(id) {
    await api.delete(
        `/inventaire/etages/${id}/`
    );
}