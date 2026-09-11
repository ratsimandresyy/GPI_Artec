import api from "./api";

export async function getEquipements() {
    const response = await api.get("/inventaire/equipements/");

    return response.data;
}