import api from "./api";

export async function login(username, password) {
    const response = await api.post("/auth/login/", {
        username: username,
        password: password,
    });

    return response.data;
}