import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';
import router from './router';

import { definirGestionSessionExpiree } from './services/api';
import { useAuthStore } from './stores/auth';

const app = createApp(App);

app.use(createPinia());
app.use(router);

/*
 * Point d'assemblage : c'est ici que l'on câble le comportement
 * attendu lorsque la session n'est plus valide.
 *
 * api.js reste ainsi indépendant du store et du routeur, ce qui évite
 * un cycle d'imports entre les services, le store et le routeur.
 */
definirGestionSessionExpiree(() => {
    useAuthStore().seDeconnecter();

    const routeCourante = router.currentRoute.value;

    // Inutile de rediriger si l'on est déjà dans l'espace public.
    if (!routeCourante.meta?.public) {
        router.push({ name: 'DashboardPublic' });
    }
});

app.mount("#app");
