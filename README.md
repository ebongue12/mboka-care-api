# 🏥 Mboka Care - Backend API

Backend Django REST Framework pour l'application Mboka Care, un système de gestion de dossiers médicaux électroniques.

## 🚀 Fonctionnalités

- ✅ Authentification JWT avec numéro de téléphone
- ✅ Gestion des patients et dossiers médicaux
- ✅ Gestion des docteurs et hôpitaux
- ✅ Système de rappels médicaux
- ✅ Partage sécurisé de dossiers médicaux
- ✅ Notifications en temps réel
- ✅ Synchronisation multi-appareils

## 📦 Technologies

- **Framework** : Django 5.0.1
- **API** : Django REST Framework 3.14.0
- **Base de données** : PostgreSQL
- **Authentification** : JWT (Simple JWT)
- **Serveur** : Gunicorn + WhiteNoise

## 🛠️ Installation Locale
```bash
# Cloner le repo
git clone https://github.com/ebongue12/mboka-care-api.git
cd mboka-care-api

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer dépendances
pip install -r requirements.txt

# Variables d'environnement
export DJANGO_SETTINGS_MODULE=config.settings.dev
export SECRET_KEY=your-secret-key
export DEBUG=True

# Migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser

# Lancer serveur
python manage.py runserver
```

## 🌐 Déploiement

### Render.com (Recommandé)

1. Créer un Web Service sur Render
2. Connecter ce repository GitHub
3. Configuration :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn config.wsgi:application`
4. Ajouter PostgreSQL database
5. Variables d'environnement :
   - `DJANGO_SETTINGS_MODULE=config.settings.prod`
   - `SECRET_KEY=<votre-clé>`
   - `DATABASE_URL=<postgres-url>`
   - `DEBUG=False`

## 📱 Applications Django

- `apps.accounts` - Gestion utilisateurs
- `apps.patients` - Dossiers patients
- `apps.doctors` - Profils médecins
- `apps.hospitals` - Hôpitaux
- `apps.medical` - Dossiers médicaux
- `apps.reminders` - Rappels
- `apps.sharing` - Partage de dossiers
- `apps.subscriptions` - Abonnements
- `apps.notifications` - Notifications
- `apps.health_priority` - Priorités santé
- `apps.sync` - Synchronisation

## 👥 Auteur

**Ebongue** - [GitHub](https://github.com/ebongue12)

## 📄 License

MIT License
