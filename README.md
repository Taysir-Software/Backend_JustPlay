# 🎯 JustPlay – Backend API

Ce dépôt contient le code backend de l'application **JustPlay**, une plateforme de réservation et de gestion multi-activités (sport, bien-être, formation, spectacle, etc.), développée avec **Django** et **Django REST Framework**.

---

## 🚀 Fonctionnalités principales

- 🔐 Authentification sécurisée (JWT)
- 📅 Gestion des créneaux et réservations
- 💳 Paiement en ligne (Stripe, PayPal, etc.)
- 📊 Statistiques par exploitant et admin
- 📦 API RESTful pour le frontend React
- 🗓️ Synchronisation des calendriers via webhooks
- 📁 Uploads médias pour les activités

---

## 📂 Structure du projet

justplay_backend/
├── api/ # App principale avec modèles, vues, serializers
│ ├── migrations/
│ ├── models.py
│ ├── serializers.py
│ ├── views.py
│ └── urls.py
├── justplay_backend/ # Configuration Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md


---

## 🛠️ Installation locale

### 1. Cloner le projet

```bash
git clone https://github.com/justplay-org/JustPlay_Backend.git
cd JustPlay_Backend
```

### 2. Créer et activer un environnement virtuel

```bash
python -m venv env
env\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Appliquer les migrations

```bash
python manage.py migrate
```

### 5. Lancer le serveur de développement

```bash
python manage.py runserver
```

## ✅ Variables d'environnement

Crée un fichier .env à la racine avec les variables suivantes :

SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=...

