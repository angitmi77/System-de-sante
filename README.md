# Système de Gestion des Rendez-vous Médicaux

Un système complet de gestion des rendez-vous médicaux développé en Python avec interface graphique Tkinter.

## 🚀 Fonctionnalités

### 👨‍💼 Espace Administrateur
- Connexion sécurisée (admin/admin)
- Gestion des médecins (ajout/suppression)
- Vue d'ensemble du système

### 👤 Espace Patient
- Création de compte avec validation complète
- Connexion sécurisée
- Prise de rendez-vous intelligente avec sélecteurs
- Consultation de ses rendez-vous
- **Tous les champs obligatoires** lors de l'inscription

### 👨‍⚕️ Espace Médecin
- Connexion sécurisée
- Agenda détaillé avec informations patients
- Gestion des créneaux disponibles
- Rendez-vous urgents mis en évidence

## 🔧 Prérequis

**Aucune dépendance externe !** 
- Python 3.x avec Tkinter (inclus par défaut)
- SQLite (inclus avec Python)

## 🛠️ Installation et Lancement

1. Cloner le repository :
```bash
git clone https://github.com/votre-username/sys-de-sante.git
cd sys-de-sante
```

2. Lancer l'application :
```bash
python main.py
```

## 📋 Comptes de Test

- **Administrateur :** admin / admin
- **Patients :** Créés via l'interface d'inscription
- **Médecins :** Ajoutés par l'administrateur

## ⏰ Contraintes Métier

### Créneaux horaires
- **Matin :** 8h00 → 11h30 (créneaux de 30 min)
- **Pause déjeuner :** 12h00 → 13h00 (automatiquement exclue)
- **Après-midi :** 13h00 → 16h30 (créneaux de 30 min)

### Validations
- Dates passées interdites
- Anticipation minimale de 30 minutes
- Validation complète des données (nom, téléphone, âge, adresse)
- Prévention automatique des conflits de créneaux

## 📁 Structure du Projet

```
sys-de-sante/
├── main.py          # Interface d'accueil
├── admin.py         # Espace administrateur
├── patient.py       # Espace patient
├── medecin.py       # Espace médecin
├── hopital.db       # Base de données SQLite (créée automatiquement)
└── README.md        # Ce fichier
```

## 🏥 Spécialités Médicales

1. Radiologue
2. Anesthésiste réanimateur
3. Cardiologue
4. Dentiste

## 🎨 Interface

- Design sombre uniforme
- Sélecteurs graphiques (pas de saisie manuelle pour date/heure)
- Messages d'erreur clairs et informatifs
- Fenêtres centrées automatiquement

## 📊 Base de Données

Tables créées automatiquement :
- `admin` - Authentification administrateur
- `patients` - Informations patients (tous les champs obligatoires)
- `medecins` - Médecins avec spécialités
- `rendez_vous` - Planification avec statuts
- `creneaux_disponibles` - Disponibilités médecins

## 🧪 Test du Système

1. Lancer `python main.py`
2. Tester chaque espace :
   - Admin : Ajouter un médecin
   - Patient : Créer un compte (tous les champs requis) et prendre RDV
   - Médecin : Se connecter et voir l'agenda

## 📝 Licence

Projet éducatif développé avec Python, Tkinter et SQLite.

---

**Développé avec Python 3 + Tkinter + SQLite**