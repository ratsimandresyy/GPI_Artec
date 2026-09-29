import axios from "axios";

const api = axios.create({
    baseURL: "http://127.0.0.1:8000/api",
    headers: {
        "Content-Type": "application/json",
    },
});

/**
 * Décodage (sans vérification de signature) du payload d'un JWT.
 * Retourne null si le token est malformé.
 */
function decodeJwt(token) {
    try {
        const base64Url = token.split(".")[1];
        if (!base64Url) return null;

        const base64 = base64Url
            .replace(/-/g, "+")
            .replace(/_/g, "/");

        const json = decodeURIComponent(
            atob(base64)
                .split("")
                .map(
                    (c) =>
                        "%" +
                        ("00" + c.charCodeAt(0).toString(16)).slice(-2)
                )
                .join("")
        );

        return JSON.parse(json);
    } catch {
        return null;
    }
}

/**
 * Vrai si le token est expiré (claim 'exp' passé) ou illisible.
 * Un payload sans 'exp' est considéré comme valide.
 */
function estExpire(token) {
    const payload = decodeJwt(token);

    if (!payload || typeof payload.exp !== "number") {
        // Token illisible : on le traite comme invalide pour éviter
        // d'envoyer un header Authorization qui provoquerait un 401.
        return !payload;
    }

    // 'exp' est en secondes ; on retire 30s de marge.
    return payload.exp * 1000 <= Date.now() + 30000;
}

/*
 * Gestionnaire de fin de session.
 *
 * api.js ne connaît ni le store Pinia ni le routeur : les importer
 * ici créerait un cycle
 * (api.js -> stores/auth.js -> services/authService.js -> api.js).
 *
 * Le gestionnaire est donc injecté depuis main.js, qui est le point
 * d'assemblage de l'application.
 */
let surSessionExpiree = null;

/**
 * Enregistre le comportement à appliquer lorsque la session n'est plus
 * valide (token expiré ou 401 renvoyé par l'API).
 *
 * @param {Function} gestionnaire
 */
export function definirGestionSessionExpiree(gestionnaire) {
    surSessionExpiree = gestionnaire;
}

function notifierSessionExpiree() {
    if (typeof surSessionExpiree === "function") {
        surSessionExpiree();
    }
}

//Ajoute automatiquement le token JWT aux requetes
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("accessToken");

        // On n'attache un token que s'il est présent ET non expiré.
        // Un token expiré ferait échouer l'authentification JWT (401)
        // même sur les endpoints publics (list/retrieve en AllowAny).
        if (token) {
            if (estExpire(token)) {
                // Token expiré : on purge et on prévient l'application
                // pour que le store cesse de présenter l'utilisateur
                // comme connecté.
                localStorage.removeItem("accessToken");
                localStorage.removeItem("refreshToken");
                localStorage.removeItem("user");

                notifierSessionExpiree();
            } else {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// En cas de 401 (token expiré ou invalidé côté serveur), la session est
// purgée : les requêtes suivantes partent en anonyme, le store est
// remis à zéro et l'utilisateur revient à l'espace public.
api.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error?.response?.status;
        const url = error?.config?.url ?? "";

        if (status === 401) {
            // Ne pas purger lors d'une tentative de connexion échouée.
            const estConnexion = url.includes("/auth/login/");

            if (!estConnexion) {
                localStorage.removeItem("accessToken");
                localStorage.removeItem("refreshToken");
                localStorage.removeItem("user");

                notifierSessionExpiree();
            }
        }

        return Promise.reject(error);
    }
);

export default api;