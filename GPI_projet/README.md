# GPI - Gestion du Parc Informatique

## 📋 Description

Système de gestion du parc informatique permettant aux administrateurs de gérer les équipements, leur localisation, les tickets de panne, et aux visiteurs de signaler des problèmes et consulter le plan graphique.

## 🏗️ Architecture

### Backend (Django + DRF)
- Framework : Django 6.0.7
- API REST : Django REST Framework
- Authentification : JWT (SimpleJWT)
- Base de données : SQLite
- Architecture : MVC avec services métier séparés

### Frontend (Vue 3)
- Framework : Vue 3 (Composition API)
- Build tool : Vite
- State management : Pinia
- Routing : Vue Router
- HTTP client : Axios
- Styling : CSS scoped + Bootstrap 5

## 📁 Structure du projet

```
GPI_projet/
├── backend/              # Django REST API
│   ├── accounts/          # Gestion utilisateurs et auth
│   ├── audit/             # Import WinAudit
│   ├── config/            # Configuration Django
│   ├── dashboard/         # Dashboard et stats
│   ├── inventaire/        # Gestion du parc
│   │   ├── models/        # Modèles de données
│   │   ├── services/      # Logique métier
│   │   ├── tests/         # Tests
│   │   └── ...
│   ├── manage.py
│   └── requirements.txt
├── frontend/             # Vue 3 application
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   ├── composables/   # Logic réutilisable
│   │   ├── layouts/       # Mises en page
│   │   ├── pages/         # Pages de l'application
│   │   ├── router/        # Configuration des routes
│   │   ├── services/      # Services API
│   │   ├── stores/        # Gestion d'état (Pinia)
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
└── Plans_de_conception_du_GPI/  # Diagrammes PlantUML
    ├── Classe/
    ├── User_case/
    └── Activity/
```

## 🚀 Installation

### Prérequis
- Python 3.x
- Node.js 18+
- npm

### Backend

```bash
cd backend

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Démarrer le serveur
python manage.py runserver
```

L'API sera accessible sur `http://127.0.0.1:8000`

### Frontend

```bash
cd frontend

# Installer les dépendances
npm install

# Démarrer en développement
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

## 📊 Fonctionnalités

### Gestion du parc
- ✅ CRUD Bâtiments, Étages, Salles
- ✅ CRUD Équipements
- ✅ Recherche d'équipements
- ✅ Filtres et tri avancés
- ✅ Pagination
- ✅ Gestion du stock
- ✅ Localisation visuelle sur plans

### Tickets de panne
- ✅ Création de tickets (titre, type, priorité)
- ✅ Prise en charge par les admins
- ✅ Résolution avec commentaire
- ✅ Formulaire public pour les visiteurs
- ✅ Types : Maintenance, Réclamation
- ✅ Priorités : Basse, Normale, Haute, Critique

### Audits WinAudit
- ✅ Import automatique des fichiers WinAudit
- ✅ Visualisation des données techniques
- ✅ Données brutes JSON
- ✅ Filtres par équipement

### Utilisateurs
- ✅ CRUD utilisateurs (admin)
- ✅ Profil utilisateur
- ✅ Rôles : ADMIN, USER

### Visiteurs
- ✅ Formulaire de signalement de ticket (sans authentification)
- ✅ Plan graphique en lecture seule
- ✅ Pas de connexion requise

### Notifications
- ✅ Système de notifications toast
- ✅ Types : success, error, warning, info
- ✅ Auto-suppression

## 🔐 Rôles et permissions

### ADMIN
- Connexion via login
- Accès complet à toutes les fonctionnalités
- CRUD sur les ressources
- Gestion des tickets
- Drag & drop sur les plans
- Export de données

### USER (Visiteur)
- Pas de connexion possible
- Accès au formulaire de signalement de ticket
- Accès au plan graphique en lecture seule

## 🎨 Architecture et principes

### Principes SOLID appliqués

#### Single Responsibility Principle (SRP)
- Composants : Chaque composant a une responsabilité unique
- Services : Chaque service gère un domaine métier spécifique
- Composables : Chaque composable encapsule une logique réutilisable

#### Open/Closed Principle (OCP)
- Composants ouverts à l'extension via props
- Services fermés à la modification sans respecter les interfaces

#### Liskov Substitution Principle (LSP)
- Composants substituables sans casser l'application

#### Interface Segregation Principle (ISP)
- Services exposent uniquement les méthodes nécessaires
- Composants n'exposent que les props nécessaires

#### Dependency Inversion Principle (DIP)
- Services dépendent d'abstractions et non d'implémentations concrètes

### Séparation des responsabilités

- **Backend** : Validation, logique métier, persistance
- **Frontend** : Présentation, interaction utilisateur, état UI
- **Services métier** : Logique métier réutilisable (PanneService, StockService, etc.)

## 📡 API

### Base URL
`http://127.0.0.1:8000/api`

### Endpoints principaux

| Ressource | GET | POST | PUT | DELETE |
|-----------|-----|------|-----|--------|
| Authentification | ✅ | ✅ | ❌ | ❌ |
| Utilisateurs | ✅ | ✅ | ✅ | ✅ |
| Bâtiments | ✅ | ✅ | ✅ | ✅ |
| Étages | ✅ | ✅ | ✅ | ✅ |
| Salles | ✅ | ✅ | ✅ | ✅ |
| Équipements | ✅ | ✅ | ✅ | ✅ |
| Tickets | ✅ | ✅ | ❌ | ❌ |
| Actions tickets | ✅ | ✅ | ❌ | ❌ |
| Stock | ✅ | ✅ | ❌ | ❌ |
| Positions | ✅ | ✅ | ✅ | ✅ |
| Audits | ✅ | ❌ | ❌ | ❌ |
| Dashboard | ✅ | ❌ | ❌ | ❌ |

## 🧪 Tests

### Backend
```bash
cd backend
python manage.py test
```

### Frontend
Les tests E2E sont à implémenter.

## 📝 Conformité avec les diagrammes de conception

### Classe
- ✅ TicketPanne avec titre, type, priorité
- ✅ Statuts : OUVERT, EN_COURS, RESOLU, ANNULE
- ✅ Types : MAINTENANCE, RECLAMATION
- ✅ Priorités : BASSE, NORMALE, HAUTE, CRITIQUE
- ✅ États d'équipement : EN_SERVICE, EN_PANNE, EN_MAINTENANCE, HORS_SERVICE
- ✅ Situations : AFFECTE, EN_STOCK
- ✅ Conditions du stock : NEUF, OCCASION, RECONDITIONNE

### User case
- ✅ Authentification ADMIN
- ✅ Visiteur sans authentification
- ✅ Création de ticket par visiteur
- ✅ Consultation du plan par visiteur
- ✅ Gestion complète par ADMIN

### Activity
- ✅ Workflow de ticket (OUVERT → EN_COURS → RESOLU)
- ✅ Modification de l'état de l'équipement lors de la résolution
- ✅ Enregistrement des dates et commentaires

## 🔗 Technologies

### Backend
- Django 6.0.7
- Django REST Framework
- SimpleJWT
- SQLite

### Frontend
- Vue 3
- Vite
- Pinia
- Vue Router
- Axios
- Bootstrap 5

## 📄 License

Projet interne de gestion de parc informatique.

## 👥 Contributeurs

- Cognition (Développement initial)
- Équipe projet GPI

## 📞 Support

Pour toute question sur le projet, contacter l'équipe responsable.
