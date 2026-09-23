import api from "./api";

export async function getUtilisateurs() {
    const response = await api.get("/auth/users/");
    return response.data;
}

export async function getUtilisateur(id) {
    const response = await api.get(`/auth/users/${id}/`);
    return response.data;
}

export async function creerUtilisateur(donnees) {
    const response = await api.post("/auth/users/", donnees);
    return response.data;
}

export async function modifierUtilisateur(id, donnees) {
    const response = await api.put(`/auth/users/${id}/`, donnees);
    return response.data;
}

export async function supprimerUtilisateur(id) {
    await api.delete(`/auth/users/${id}/`);
}