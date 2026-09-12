import api from "./api";


// Récupérer toutes les salles
export async function getSalles() {
    const response = await api.get("/inventaire/salles/");
    return response.data;
}


// Récupérer une salle par son ID
export async function getSalle(id) {
    const response = await api.get(
        `/inventaire/salles/${id}/`
    );

    return response.data;
}


// Créer une salle
export async function creerSalle(donnees) {
    const response = await api.post(
        "/inventaire/salles/",
        donnees
    );

    return response.data;
}


// Modifier une salle
export async function modifierSalle(id, donnees) {
    const response = await api.put(
        `/inventaire/salles/${id}/`,
        donnees
    );

    return response.data;
}


// Supprimer une salle
export async function supprimerSalle(id) {
    await api.delete(
        `/inventaire/salles/${id}/`
    );
}