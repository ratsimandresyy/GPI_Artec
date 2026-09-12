import api from "./api";

export async function getEquipements() {
    const response = await api.get("/inventaire/equipements/");

    return response.data;
}

/** recherche les equipement a partir des terme */

export async function rechercherEquipement(terme) {
    const response = await api.get(
        "/inventaire/equipements/rechercher/", {params: { q: terme,},}
    );

    return response.data;
}

export async function getEquipement(id) {
    const response = await api.get(`/inventaire/equipements/${id}/`);

    return response.data;
}

// Récupérer les équipements d'une salle
export async function getEquipementsParSalle(salleId) {
    const response = await api.get(
        "/inventaire/equipements/"
    );

    // L'API retourne actuellement tous les équipements.
    // On filtre ceux appartenant à la salle sélectionnée.
    return response.data.filter(
        (equipement) =>
            String(equipement.salle) === String(salleId)
    );
}