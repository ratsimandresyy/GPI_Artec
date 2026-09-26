# GPI - Backend

## 📋 Description

API REST Django pour le système de gestion du parc informatique (GPI).

## 🚀 Stack technique

- **Framework** : Django 6.0.7
- **API** : Django REST Framework
- **Base de données** : SQLite (configurable)
- **Authentification** : JWT (SimpleJWT)
- **Python** : 3.x

## 📁 Structure du projet

```
backend/
├── accounts/              # Gestion des utilisateurs et authentification
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
├── audit/                # Importation et gestion des audits WinAudit
│   ├── models/
│   │   ├── models_connexion_audit.py
│   │   └── models_rapportAudit.py
│   ├── services.py
│   ├── views.py
│   ├── serializers.py
│   ├── parser.py
│   ├── importer.py
│   ├── watcher.py
│   └── urls.py
├── config/                # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── dashboard/             # Dashboard et statistiques
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
├── inventaire/             # Gestion du parc informatique
│   ├── models/
│   │   ├── batiment.py
│   │   ├── equipement.py
│   │   ├── etage.py
│   │   ├── plan.py
│   │   ├── position.py
│   │   ├── salle.py
│   │   └── ticket_panne.py
│   ├── services/
│   │   ├── equipement_service.py
│   │   ├── localisation_service.py
│   │   ├── panne_service.py
│   │   ├── recherche_service.py
│   │   └── stock_service.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

## 🔧 Installation

```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🚀 Démarrage

```bash
python manage.py runserver
```

L'API sera accessible sur `http://127.0.0.1:8000`

## 🗄️ Migrations

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

## 🧪 Tests

```bash
# Lancer tous les tests
python manage.py test

# Lancer les tests d'une app spécifique
python manage.py test inventaire
python manage.py test audit
python manage.py test accounts
```

## 📊 Modèles de données

### Utilisateur (accounts.User)
- Hérite de Django AbstractUser
- Rôle : ADMIN, USER
- JWT pour l'authentification

### Inventaire

#### Batiment
- Nom
- Description

#### Etage
- Nom
- Bâtiment (ForeignKey)

#### Salle
- Nom
- Étage (ForeignKey)
- Plan (ForeignKey)

#### Plan
- Image
- Salle (ForeignKey)

#### Position
- X, Y (coordonnées)
- Plan (ForeignKey)
- Équipement (ForeignKey)

#### Equipement
- Nom (unique)
- Type (ORDINATEUR)
- Numéro d'inventaire (unique)
- Numéro de série (unique)
- Fabricant
- Modèle
- Adresse IP
- Adresse MAC
- Salle (ForeignKey)
- État : EN_SERVICE, EN_PANNE, EN_MAINTENANCE, HORS_SERVICE
- Situation : AFFECTE, EN_STOCK
- Condition du stock : NEUF, OCCASION, RECONDITIONNE

#### TicketPanne
- Équipement (ForeignKey)
- Titre
- Type : MAINTENANCE, RECLAMATION
- Priorité : BASSE, NORMALE, HAUTE, CRITIQUE
- Date de signalement
- Description
- Statut : OUVERT, EN_COURS, RESOLU, ANNULE
- Date de résolution
- Commentaire de résolution

### Audit

#### RapportAudit
- Équipement (ForeignKey)
- Date d'audit
- Système d'exploitation
- Processeur
- Mémoire
- Stockage
- BIOS
- Données brutes (JSON)

#### ConnexionAudit
- Modèle pour suivre les connexions (non utilisé en frontend)

## 🔐 Permissions

### IsAdministrateurOrReadOnly
- GET, HEAD, OPTIONS : Public
- POST, PUT, DELETE, PATCH : ADMIN uniquement

### IsUserOrAdministrateur
- Authentification requise
- Accès pour USER et ADMIN

## 🎯 Services métier

### PanneService
- `declarer_panne()` : Crée un ticket et met l'équipement en EN_PANNE
- `prendre_en_charge()` : Passe le ticket en EN_COURS
- `resoudre_ticket()` : Résout le ticket et remet l'équipement en EN_SERVICE

### StockService
- Gestion des transferts au stock
- Terminer la maintenance
- Affecter un équipement

### LocalisationService
- Gestion des positions sur les plans
- Déplacement d'équipements

### EquipementService
- Logique spécifique aux équipements

### RechercheService
- Recherche avancée d'équipements

## 📡 API Endpoints

### Authentification
- `POST /api/auth/login/` - Connexion (JWT)

### Utilisateurs
- `GET /api/auth/users/` - Liste des utilisateurs
- `GET /api/auth/users/:id/` - Détail utilisateur
- `POST /api/auth/users/` - Créer utilisateur
- `PUT /api/auth/users/:id/` - Modifier utilisateur
- `DELETE /api/auth/users/:id/` - Supprimer utilisateur
- `GET /api/auth/users/me/` - Profil utilisateur connecté
- `PUT /api/auth/users/me/` - Modifier profil utilisateur connecté

### Inventaire
- `GET /api/inventaire/batiments/` - Liste des bâtiments
- `POST /api/inventaire/batiments/` - Créer bâtiment
- `PUT /api/inventaire/batiments/:id/` - Modifier bâtiment
- `DELETE /api/inventaire/batiments/:id/` - Supprimer bâtiment

- `GET /api/inventaire/etages/` - Liste des étages
- `POST /api/inventaire/etages/` - Créer étage
- `PUT /api/inventaire/etages/:id/` - Modifier étage
- `DELETE /api/inventaire/etages/:id/` - Supprimer étage

- `GET /api/inventaire/salles/` - Liste des salles
- `POST /api/inventaire/salles/` - Créer salle
- `PUT /api/inventaire/salles/:id/` - Modifier salle
- `DELETE /api/inventaire/salles/:id/` - Supprimer salle

- `GET /api/inventaire/equipements/` - Liste des équipements
- `GET /api/inventaire/equipements/:id/` - Détail équipement
- `POST /api/inventaire/equipements/` - Créer équipement
- `PUT /api/inventaire/equipements/:id/` - Modifier équipement
- `DELETE /api/inventaire/equipements/:id/` - Supprimer équipement
- `GET /api/inventaire/equipements/rechercher/` - Rechercher équipements

- `GET /api/inventaire/positions/` - Liste des positions
- `POST /api/inventaire/positions/` - Créer position
- `PUT /api/inventaire/positions/:id/` - Modifier position
- `DELETE /api/inventaire/positions/:id/` - Supprimer position

- `GET /api/inventaire/tickets-panne/` - Liste des tickets
- `POST /api/inventaire/tickets-panne/` - Créer ticket (publique)
- `POST /api/inventaire/tickets-panne/:id/prendre-en-charge/` - Prendre en charge
- `POST /api/inventaire/tickets-panne/:id/resoudre/` - Résoudre ticket

- `GET /api/inventaire/stock/` - État du stock
- `POST /api/inventaire/stock/transferer/` - Transférer au stock
- `POST /api/inventaire/stock/terminer-maintenance/` - Terminer maintenance
- `POST /api/inventaire/stock/affecter/` - Affecter équipement

### Audit
- `GET /api/audit/rapports/` - Liste des rapports d'audit
- `GET /api/audit/rapports/:id/` - Détail rapport

### Dashboard
- `GET /api/dashboard/statistiques/` - Statistiques générales
- `GET /api/dashboard/equipements/` - Équipements pour dashboard

## 🎨 Architecture

### Séparation des responsabilités

- **Models** : Définition des données et validation
- **Serializers** : Conversion API ↔ Models
- **Views** : Endpoints HTTP et permissions
- **Services** : Logique métier réutilisable

### Services métier

La logique métier est centralisée dans les services :
- `PanneService` : Gestion des tickets de panne
- `StockService` : Gestion du stock
- `LocalisationService` : Gestion des positions
- `EquipementService` : Logique spécifique aux équipements
- `RechercheService` : Recherche avancée

## 🔐 Rôles

### ADMIN
- Accès complet à l'API
- CRUD sur toutes les ressources
- Actions spécifiques (prise en charge, résolution de tickets)

### USER (Visiteur)
- Accès en lecture seule aux ressources
- Création de tickets sans authentification (via endpoint public)

## 📝 Règles de gestion

- L'utilisateur doit être authentifié pour accéder au système GPI
- En cas d'échec, nouvelle tentative possible
- Après authentification, vérification des droits
- ADMIN : accès aux fonctionnalités d'administration
- USER : accès aux fonctionnalités visiteur (lecture seule)
- Seuls les ADMIN peuvent se connecter via login
- Les visiteurs peuvent créer des tickets via formulaire public
- Les visiteurs peuvent consulter le plan graphique
- La clôture d'un ticket enregistre sa date et durée
- Le traitement d'un ticket peut modifier l'état du matériel
- Toutes les modifications sont enregistrées en base de données

## 🧪 Tests

### Tests existants
- `inventaire.tests.test_panne_service` : Tests du service de panne (5 tests)
- `inventaire.tests.test_stock_service` : Tests du service de stock (3 tests)
- `inventaire.tests.test_localisation_service` : Tests du service de localisation (5 tests)
- `inventaire.tests.test_localisation_api` : Tests API localisation (3 tests)
- `inventaire.tests.test_stock_api` : Tests API stock (4 tests)
- `inventaire.tests.test_serializers` : Tests des serializers (2 tests)

Total : 22 tests

## 📝 Notes importantes

- La base de données SQLite est stockée dans `db.sqlite3`
- Les fichiers WinAudit sont importés dans `media/audits/`
- Le watcher d'import automatique est dans `audit/watcher.py`
- Les tokens JWT expirent et nécessitent un refresh
- La validation des données est à la fois côté backend (Django) et frontend

## 🔗 Intégration avec le frontend

L'API REST est consommée par le frontend Vue.js disponible sur :
- Base URL : `http://127.0.0.1:8000/api`
- Authentification via JWT Bearer token
- CORS configuré pour autoriser le frontend

## 📄 License

Projet interne de gestion de parc informatique.
