# GPI - Frontend

## 📋 Description

Interface utilisateur du système de gestion du parc informatique (GPI).

## 🚀 Stack technique

- **Framework** : Vue 3 (Composition API)
- **Build tool** : Vite
- **State management** : Pinia
- **Routing** : Vue Router
- **HTTP client** : Axios
- **Styling** : CSS (scoped), Bootstrap 5 (installé)

## 📁 Structure du projet

```
frontend/
├── src/
│   ├── components/          # Composants réutilisables
│   │   ├── EquipementForm.vue
│   │   ├── Filters.vue
│   │   ├── NotificationToast.vue
│   │   ├── Pagination.vue
│   │   ├── PlanViewer.vue
│   │   └── TableSort.vue
│   ├── composables/          # Logic réutilisable (Pinia composables)
│   │   └── useTableData.js
│   ├── layouts/              # Mises en page
│   │   └── MainLayout.vue
│   ├── pages/                # Pages de l'application
│   │   ├── Audits.vue
│   │   ├── Batiments.vue
│   │   ├── Dashboard.vue
│   │   ├── EquipementDetail.vue
│   │   ├── Equipements.vue
│   │   ├── Etages.vue
│   │   ├── Localisation.vue
│   │   ├── Login.vue
│   │   ├── PlanPublic.vue
│   │   ├── Profile.vue
│   │   ├── Salles.vue
│   │   ├── TicketPublic.vue
│   │   ├── Tickets.vue
│   │   └── Utilisateurs.vue
│   ├── router/               # Configuration des routes
│   │   └── index.js
│   ├── services/              # Services API
│   │   ├── api.js
│   │   ├── auditService.js
│   │   ├── auth.js
│   │   ├── batimentService.js
│   │   ├── dashboardService.js
│   │   ├── equipementService.js
│   │   ├── etageService.js
│   │   ├── localisationService.js
│   │   ├── salleService.js
│   │   ├── stockService.js
│   │   ├── ticketService.js
│   │   └── utilisateurService.js
│   ├── stores/                # Gestion d'état (Pinia)
│   │   ├── auth.js
│   │   └── notifications.js
│   ├── App.vue
│   └── main.js
├── public/
├── index.html
├── package.json
└── vite.config.js
```

## 🔧 Installation

```bash
npm install
```

## 🚀 Démarrage

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

## 🏗️ Build pour production

```bash
npm run build
```

## 📄 Pages de l'application

### Pages publiques (sans authentification)
- `/login` - Connexion administrateur
- `/signaler` - Formulaire de signalement de ticket (visiteur)
- `/plan` - Plan graphique du système (visiteur)

### Pages admin (authentification requise)
- `/dashboard` - Tableau de bord
- `/equipements` - Gestion des équipements
- `/equipements/:id` - Détail d'un équipement
- `/batiments` - Gestion des bâtiments
- `/batiments/:batimentId/etages` - Étages d'un bâtiment
- `/etages/:etageId/salles` - Salles d'un étage
- `/salles/:salleId/equipements` - Équipements d'une salle
- `/localisation` - Localisation sur les plans
- `/audits` - Rapports d'audit WinAudit
- `/utilisateurs` - Gestion des utilisateurs
- `/tickets` - Gestion des tickets de panne
- `/profile` - Profil utilisateur

## 🔐 Rôles et permissions

### ADMIN
- Accès complet à toutes les pages
- CRUD sur les équipements, bâtiments, étages, salles
- Gestion des tickets (création, prise en charge, résolution)
- Gestion des utilisateurs
- Drag & drop sur les plans
- Export de données

### USER (Visiteur)
- Accès limité au formulaire de signalement de ticket
- Accès au plan graphique en lecture seule
- Pas de connexion possible

## 🎨 Composants réutilisables

### Filters.vue
Composant de filtres dynamiques avec support pour :
- Filtres de type select
- Filtres de type text
- Réinitialisation

### Pagination.vue
Composant de pagination avec :
- Navigation précédent/suivant
- Sélecteur d'éléments par page
- Affichage du nombre total d'éléments

### TableSort.vue
Composant de tri de colonnes avec :
- Indicateur visuel de tri
- Support de l'ordre ascendant/descendant

### NotificationToast.vue
Système de notifications avec :
- 4 types : success, error, warning, info
- Auto-suppression configurable
- Animation d'entrée/sortie
- Empilement des notifications

### PlanViewer.vue
Composant avancé pour la visualisation des plans avec :
- Affichage des plans image
- Positionnement des équipements
- Drag & drop pour les admins
- Lien avec le stock

### EquipementForm.vue
Formulaire modal pour la création/modification d'équipements avec :
- Validation des champs
- Gestion conditionnelle des champs (salle vs condition_stock)

## 🔧 Composables

### useTableData.js
Composable pour la logique de tableau avec :
- Pagination
- Filtrage
- Tri
- Réutilisation possible dans n'importe quelle page de liste

## 📊 Services API

Tous les services utilisent Axios avec une configuration commune :
- Base URL : `http://127.0.0.1:8000/api`
- Authorization header automatique depuis localStorage
- Gestion des erreurs centralisée

## 🛠️ Développement

### Ajouter une nouvelle page

1. Créer le fichier dans `src/pages/`
2. Ajouter la route dans `src/router/index.js`
3. Ajouter le lien dans `src/layouts/MainLayout.vue` si nécessaire

### Ajouter un nouveau service API

1. Créer le fichier dans `src/services/`
2. Importer et utiliser `api` pour les requêtes HTTP
3. Gérer les erreurs de manière cohérente

### Ajouter un nouveau composant

1. Créer le fichier dans `src/components/`
2. Importer et utiliser dans les pages
3. Appliquer les principes SOLID

## 🧪 Tests

Les tests sont à implémenter. Voici les zones à tester :
- Tests unitaires des composants
- Tests E2E des flux critiques
- Tests d'intégration API

## 📝 Notes importantes

- Le backend Django doit être démarré sur `http://127.0.0.1:8000`
- Les tokens JWT sont stockés dans `localStorage`
- Les filtres et pagination sont côté client (frontend)
- Le backend fournit les données brutes pour les exports

## 🔗 Intégration avec le backend

L'application se connecte à l'API REST Django disponible sur :
- Base URL : `http://127.0.0.1:8000/api`
- Endpoints documentés dans les services correspondants

## 📄 License

Projet interne de gestion de parc informatique.
