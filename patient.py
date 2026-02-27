import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import calendar
import re

class EspacePatient:
    def __init__(self, root):
        self.root = root
        self.root.title("Espace Patient")
        self.root.geometry("600x500")
        self.root.configure(bg="#2c2c2c")
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        # Initialiser la base de données
        self.init_database()
        
        # Patient connecté
        self.patient_connecte = None
        
        # Créer l'interface de connexion
        self.creer_interface_connexion()
    
    def centrer_fenetre(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def init_database(self):
        self.conn = sqlite3.connect('hopital.db')
        self.cursor = self.conn.cursor()
        
        # Créer les tables si elles n'existent pas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_complet TEXT NOT NULL,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL,
                telephone TEXT,
                age INTEGER,
                adresse TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rendez_vous (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                medecin_id INTEGER,
                date_rdv TEXT NOT NULL,
                heure_rdv TEXT NOT NULL,
                urgent INTEGER DEFAULT 0,
                statut TEXT DEFAULT 'confirmé',
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (medecin_id) REFERENCES medecins (id)
            )
        ''')
        
        self.conn.commit()
    
    def generer_heures_disponibles(self, heures_occupees=None):
        """Générer les créneaux horaires disponibles (8h-16h, pause 12h, créneaux 30min)"""
        if heures_occupees is None:
            heures_occupees = []
        
        heures_disponibles = []
        
        # Matin : 8h00 à 11h30 (créneaux de 30 min)
        for heure in range(8, 12):
            for minute in [0, 30]:
                heure_str = f"{heure:02d}:{minute:02d}"
                if heure_str not in heures_occupees:
                    heures_disponibles.append(heure_str)
        
        # Après-midi : 13h00 à 16h30 (créneaux de 30 min)
        for heure in range(13, 17):
            for minute in [0, 30]:
                if heure == 16 and minute > 30:  # Arrêt à 16h30
                    break
                heure_str = f"{heure:02d}:{minute:02d}"
                if heure_str not in heures_occupees:
                    heures_disponibles.append(heure_str)
        
        return heures_disponibles
    
    def valider_date(self, date_str):
        """Valider le format de date JJ/MM/AAAA et vérifier qu'elle n'est pas passée"""
        try:
            # Vérifier le format
            jour, mois, annee = date_str.split('/')
            date_obj = datetime(int(annee), int(mois), int(jour)).date()
            
            # Vérifier que ce n'est pas dans le passé
            if date_obj < datetime.now().date():
                return False, "La date ne peut pas être dans le passé"
            
            return True, date_obj
            
        except (ValueError, IndexError):
            return False, "Format de date invalide (JJ/MM/AAAA requis)"
    
    def valider_heure(self, heure_str):
        """Valider le format d'heure HH:MM et vérifier les créneaux"""
        try:
            heure, minute = heure_str.split(':')
            heure_int, minute_int = int(heure), int(minute)
            
            # Vérifier le format basique
            if not (0 <= heure_int <= 23 and 0 <= minute_int <= 59):
                return False, "Heure invalide"
            
            # Vérifier les créneaux autorisés
            if minute_int not in [0, 30]:
                return False, "Seuls les créneaux de 30 minutes sont autorisés (XX:00 ou XX:30)"
            
            # Vérifier les heures d'ouverture
            if not ((8 <= heure_int < 12) or (13 <= heure_int <= 16)):
                return False, "Heures d'ouverture : 8h-12h et 13h-16h30"
            
            # Vérifier pause déjeuner
            if heure_int == 12:
                return False, "Pause déjeuner de 12h à 13h"
            
            # Vérifier limite après-midi
            if heure_int == 16 and minute_int > 30:
                return False, "Dernier créneau à 16h30"
                
            return True, heure_str
            
        except (ValueError, IndexError):
            return False, "Format d'heure invalide (HH:MM requis)"
    
    def obtenir_creneaux_occupes(self, medecin_id, date_str):
        """Obtenir les créneaux déjà occupés pour un médecin à une date donnée"""
        self.cursor.execute('''
            SELECT heure_rdv FROM rendez_vous
            WHERE medecin_id = ? AND date_rdv = ? AND statut != 'annulé'
        ''', (medecin_id, date_str))
        
        resultats = self.cursor.fetchall()
        return [resultat[0] for resultat in resultats]
    
    def obtenir_creneaux_definis_medecin(self, medecin_id, date_str):
        """Obtenir les créneaux définis par le médecin pour une date donnée"""
        # Récupérer les créneaux définis comme disponibles par le médecin
        self.cursor.execute('''
            SELECT heure_debut, heure_fin FROM creneaux_disponibles
            WHERE medecin_id = ? AND date_creneau = ? AND disponible = 1
            ORDER BY heure_debut
        ''', (medecin_id, date_str))
        
        creneaux_definis = self.cursor.fetchall()
        
        # Si aucun créneau n'est défini, retourner les créneaux par défaut
        if not creneaux_definis:
            return self.generer_heures_disponibles()
        
        # Générer les créneaux de 30 minutes dans chaque plage définie
        heures_disponibles = []
        for debut_str, fin_str in creneaux_definis:
            try:
                debut = datetime.strptime(debut_str, "%H:%M")
                fin = datetime.strptime(fin_str, "%H:%M")
                
                # Générer des créneaux de 30 minutes
                creneau_actuel = debut
                while creneau_actuel < fin:
                    heure_str = creneau_actuel.strftime("%H:%M")
                    heures_disponibles.append(heure_str)
                    creneau_actuel += timedelta(minutes=30)
                    
            except ValueError:
                continue
        
        return sorted(heures_disponibles)
    
    # ============ VALIDATION DES DONNÉES ============
    def valider_nom_complet(self, nom):
        """Valider le nom complet (lettres, espaces, tirets uniquement)"""
        if not nom or not nom.strip():
            return False, "Le nom complet ne peut pas être vide"
        
        nom = nom.strip()
        if len(nom) < 2:
            return False, "Le nom complet doit contenir au moins 2 caractères"
        
        if len(nom) > 50:
            return False, "Le nom complet ne peut pas dépasser 50 caractères"
        
        # Seules lettres, espaces, tirets et apostrophes autorisés
        if not re.match(r"^[a-zA-ZÀ-ÿ\s\-']+$", nom):
            return False, "Le nom ne peut contenir que des lettres, espaces, tirets et apostrophes"
        
        return True, nom
    
    def valider_nom_utilisateur(self, username):
        """Valider le nom d'utilisateur (lettres et chiffres uniquement)"""
        if not username or not username.strip():
            return False, "Le nom d'utilisateur ne peut pas être vide"
        
        username = username.strip()
        if len(username) < 3:
            return False, "Le nom d'utilisateur doit contenir au moins 3 caractères"
        
        if len(username) > 20:
            return False, "Le nom d'utilisateur ne peut pas dépasser 20 caractères"
        
        # Seules lettres et chiffres autorisés
        if not re.match(r"^[a-zA-Z0-9]+$", username):
            return False, "Le nom d'utilisateur ne peut contenir que des lettres et chiffres"
        
        return True, username.lower()
    
    def valider_mot_de_passe(self, password):
        """Valider le mot de passe (minimum 4 caractères)"""
        if not password:
            return False, "Le mot de passe ne peut pas être vide"
        
        if len(password) < 4:
            return False, "Le mot de passe doit contenir au moins 4 caractères"
        
        if len(password) > 30:
            return False, "Le mot de passe ne peut pas dépasser 30 caractères"
        
        return True, password
    
    def valider_telephone(self, telephone):
        """Valider le numéro de téléphone (format français)"""
        if not telephone or not telephone.strip():
            return False, "Le numéro de téléphone ne peut pas être vide"
        
        telephone = telephone.strip().replace(" ", "").replace("-", "").replace(".", "")
        
        # Format français : 10 chiffres commençant par 0
        if not re.match(r"^0[1-9]\d{8}$", telephone):
            return False, "Format de téléphone invalide (ex: 0123456789)"
        
        # Formater le numéro
        formatted = f"{telephone[:2]} {telephone[2:4]} {telephone[4:6]} {telephone[6:8]} {telephone[8:]}"
        return True, formatted
    
    def valider_age(self, age_str):
        """Valider l'âge (nombre entre 1 et 120)"""
        if not age_str or not age_str.strip():
            return False, "L'âge ne peut pas être vide"
        
        try:
            age = int(age_str.strip())
            if age < 1:
                return False, "L'âge doit être supérieur à 0"
            if age > 120:
                return False, "L'âge doit être inférieur à 120 ans"
            return True, age
        except ValueError:
            return False, "L'âge doit être un nombre entier"
    
    def valider_adresse(self, adresse):
        """Valider l'adresse"""
        if not adresse or not adresse.strip():
            return False, "L'adresse ne peut pas être vide"
        
        adresse = adresse.strip()
        if len(adresse) < 5:
            return False, "L'adresse doit contenir au moins 5 caractères"
        
        if len(adresse) > 100:
            return False, "L'adresse ne peut pas dépasser 100 caractères"
        
        return True, adresse
    
    def valider_formulaire_patient(self, nom, username, password, telephone=None, age=None, adresse=None):
        """Valider un formulaire patient complet"""
        erreurs = []
        
        valid_nom, msg_nom = self.valider_nom_complet(nom)
        if not valid_nom:
            erreurs.append(f"Nom: {msg_nom}")
        
        valid_user, msg_user = self.valider_nom_utilisateur(username)
        if not valid_user:
            erreurs.append(f"Utilisateur: {msg_user}")
        
        valid_pass, msg_pass = self.valider_mot_de_passe(password)
        if not valid_pass:
            erreurs.append(f"Mot de passe: {msg_pass}")
        
        # Tous les champs sont maintenant obligatoires
        valid_tel, msg_tel = self.valider_telephone(telephone)
        if not valid_tel:
            erreurs.append(f"Téléphone: {msg_tel}")
        
        valid_age, msg_age = self.valider_age(age)
        if not valid_age:
            erreurs.append(f"Âge: {msg_age}")
        
        valid_addr, msg_addr = self.valider_adresse(adresse)
        if not valid_addr:
            erreurs.append(f"Adresse: {msg_addr}")
        
        if erreurs:
            return False, "\\n".join(erreurs)
        
        return True, "Validation réussie"
    # ============ FIN VALIDATION ============
    
    def creer_interface_connexion(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Système de gestion des rendez-vous médicaux",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c2c2c"
        )
        titre.pack(pady=30)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.root, bg="#2c2c2c")
        frame_boutons.pack(expand=True)
        
        # Style des boutons
        style_bouton = {
            "font": ("Arial", 12),
            "width": 25,
            "height": 2,
            "bg": "white",
            "fg": "black",
            "relief": "raised",
            "bd": 2
        }
        
        # Bouton Se connecter
        btn_connexion = tk.Button(
            frame_boutons,
            text="Se connecter",
            command=self.connexion_patient,
            **style_bouton
        )
        btn_connexion.pack(pady=10)
        
        # Bouton Créer un compte
        btn_creer_compte = tk.Button(
            frame_boutons,
            text="Créer un compte Patient",
            command=self.creer_compte_patient,
            **style_bouton
        )
        btn_creer_compte.pack(pady=10)
        
        # Bouton Quitter
        btn_quitter = tk.Button(
            frame_boutons,
            text="Quitter",
            command=self.quitter,
            **style_bouton
        )
        btn_quitter.pack(pady=10)
    
    def creer_compte_patient(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Créer un compte Patient",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c2c2c"
        )
        titre.pack(pady=20)
        
        # Frame pour le formulaire
        frame_form = tk.Frame(self.root, bg="#2c2c2c")
        frame_form.pack(expand=True, pady=20)
        
        # Style des labels
        style_label = {
            "font": ("Arial", 10),
            "fg": "white",
            "bg": "#2c2c2c"
        }
        
        # Champ Nom complet
        tk.Label(frame_form, text="Nom complet", **style_label).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_nom = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_nom.grid(row=0, column=1, padx=20, pady=5)
        
        # Champ Téléphone
        tk.Label(frame_form, text="Téléphone", **style_label).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_telephone = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_telephone.grid(row=1, column=1, padx=20, pady=5)
        
        # Champ Âge
        tk.Label(frame_form, text="Âge", **style_label).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_age = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_age.grid(row=2, column=1, padx=20, pady=5)
        
        # Champ Adresse
        tk.Label(frame_form, text="Adresse", **style_label).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_adresse = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_adresse.grid(row=3, column=1, padx=20, pady=5)
        
        # Champ Nom d'utilisateur
        tk.Label(frame_form, text="Nom d'utilisateur", **style_label).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_username = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_username.grid(row=4, column=1, padx=20, pady=5)
        
        # Champ Mot de passe
        tk.Label(frame_form, text="Mot de passe", **style_label).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(frame_form, font=("Arial", 10), width=30, show="*")
        self.entry_password.grid(row=5, column=1, padx=20, pady=5)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.root, bg="#2c2c2c")
        frame_boutons.pack(pady=20)
        
        # Bouton Créer mon compte
        btn_creer = tk.Button(
            frame_boutons,
            text="Créer mon compte",
            command=self.enregistrer_patient,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_creer.pack(side=tk.LEFT, padx=10)
        
        # Bouton Retour
        btn_retour = tk.Button(
            frame_boutons,
            text="Retour",
            command=self.creer_interface_connexion,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_retour.pack(side=tk.LEFT, padx=10)
    
    def enregistrer_patient(self):
        nom = self.entry_nom.get().strip()
        telephone = self.entry_telephone.get().strip()
        age = self.entry_age.get().strip()
        adresse = self.entry_adresse.get().strip()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        # Validation avec les méthodes intégrées
        valide, message = self.valider_formulaire_patient(
            nom, username, password, telephone, age, adresse
        )
        
        if not valide:
            messagebox.showerror("Erreur de validation", message)
            return
        
        # Nettoyer les données validées
        _, nom_clean = self.valider_nom_complet(nom)
        _, telephone_clean = self.valider_telephone(telephone)
        _, age_clean = self.valider_age(age)
        _, adresse_clean = self.valider_adresse(adresse)
        _, username_clean = self.valider_nom_utilisateur(username)
        
        try:
            self.cursor.execute('''
                INSERT INTO patients (nom_complet, telephone, age, adresse, nom_utilisateur, mot_de_passe)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nom_clean, telephone_clean, age_clean, adresse_clean, username_clean, password))
            self.conn.commit()
            messagebox.showinfo("Succès", "Compte patient créé avec succès")
            self.creer_interface_connexion()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà")
    
    def connexion_patient(self):
        username = simpledialog.askstring("Connexion", "Nom d'utilisateur:")
        if not username:
            return
            
        password = simpledialog.askstring("Connexion", "Mot de passe:", show='*')
        if not password:
            return
        
        self.cursor.execute('''
            SELECT id, nom_complet, telephone, age, adresse FROM patients 
            WHERE nom_utilisateur = ? AND mot_de_passe = ?
        ''', (username, password))
        
        patient = self.cursor.fetchone()
        if patient:
            self.patient_connecte = {
                "id": patient[0], 
                "nom": patient[1],
                "telephone": patient[2],
                "age": patient[3],
                "adresse": patient[4]
            }
            messagebox.showinfo("Succès", f"Bienvenue {patient[1]} !")
            self.menu_patient()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
    
    def menu_patient(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text=f"Bienvenue {self.patient_connecte['nom']}",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c2c2c"
        )
        titre.pack(pady=30)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.root, bg="#2c2c2c")
        frame_boutons.pack(expand=True)
        
        # Style des boutons
        style_bouton = {
            "font": ("Arial", 12),
            "width": 25,
            "height": 2,
            "bg": "white",
            "fg": "black",
            "relief": "raised",
            "bd": 2
        }
        
        # Bouton Prendre rendez-vous
        btn_rdv = tk.Button(
            frame_boutons,
            text="Prendre rendez-vous",
            command=self.prendre_rendez_vous,
            **style_bouton
        )
        btn_rdv.pack(pady=10)
        
        # Bouton Mes rendez-vous
        btn_mes_rdv = tk.Button(
            frame_boutons,
            text="Mes rendez-vous",
            command=self.voir_mes_rendez_vous,
            **style_bouton
        )
        btn_mes_rdv.pack(pady=10)
        
        # Bouton Déconnexion
        btn_deconnexion = tk.Button(
            frame_boutons,
            text="Déconnexion",
            command=self.deconnexion,
            **style_bouton
        )
        btn_deconnexion.pack(pady=10)
    
    def prendre_rendez_vous(self):
        # Récupérer la liste des médecins
        self.cursor.execute("SELECT id, nom_complet, specialite FROM medecins")
        medecins = self.cursor.fetchall()
        
        if not medecins:
            messagebox.showwarning("Attention", "Aucun médecin disponible")
            return
        
        # Fenêtre de sélection médecin
        fenetre_rdv = tk.Toplevel(self.root)
        fenetre_rdv.title("Prendre rendez-vous")
        fenetre_rdv.geometry("500x400")
        fenetre_rdv.configure(bg="#2c2c2c")
        
        # Liste des médecins
        tk.Label(fenetre_rdv, text="Choisir un médecin:", font=("Arial", 12, "bold"), 
                fg="white", bg="#2c2c2c").pack(pady=10)
        
        # Listbox pour les médecins
        frame_liste = tk.Frame(fenetre_rdv, bg="#2c2c2c")
        frame_liste.pack(pady=10)
        
        listbox = tk.Listbox(frame_liste, font=("Arial", 10), width=50, height=8)
        for medecin in medecins:
            listbox.insert(tk.END, f"Dr. {medecin[1]} - {medecin[2]}")
        listbox.pack()
        
        # Sélection date
        frame_date = tk.Frame(fenetre_rdv, bg="#2c2c2c")
        frame_date.pack(pady=10)
        
        tk.Label(frame_date, text="Date:", fg="white", bg="#2c2c2c").pack(side=tk.LEFT, padx=5)
        
        # Sélecteurs pour jour, mois, année
        aujourd_hui = datetime.now()
        
        # Jour (1-31)
        combo_jour = ttk.Combobox(frame_date, width=3, state="readonly")
        combo_jour['values'] = tuple(range(1, 32))
        combo_jour.set(aujourd_hui.day)
        combo_jour.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Mois (1-12)
        combo_mois = ttk.Combobox(frame_date, width=3, state="readonly")
        combo_mois['values'] = tuple(range(1, 13))
        combo_mois.set(aujourd_hui.month)
        combo_mois.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Année (année actuelle + 1)
        combo_annee = ttk.Combobox(frame_date, width=5, state="readonly")
        combo_annee['values'] = tuple(range(aujourd_hui.year, aujourd_hui.year + 2))
        combo_annee.set(aujourd_hui.year)
        combo_annee.pack(side=tk.LEFT, padx=2)
        
        # Sélection heure
        frame_heure = tk.Frame(fenetre_rdv, bg="#2c2c2c")
        frame_heure.pack(pady=10)
        
        tk.Label(frame_heure, text="Heure:", fg="white", bg="#2c2c2c").pack(side=tk.LEFT, padx=5)
        
        # Combobox pour les heures disponibles (sera mis à jour selon la date)
        combo_heure = ttk.Combobox(frame_heure, width=8, state="readonly")
        heures_initiales = self.generer_heures_disponibles()
        combo_heure['values'] = heures_initiales
        if heures_initiales:
            combo_heure.set(heures_initiales[0])
        combo_heure.pack(side=tk.LEFT, padx=5)
        
        # Fonction pour mettre à jour les heures disponibles selon la date et médecin
        def mettre_a_jour_heures(*args):
            try:
                selection = listbox.curselection()
                if not selection:
                    return
                
                jour = combo_jour.get()
                mois = combo_mois.get()
                annee = combo_annee.get()
                
                if not (jour and mois and annee):
                    return
                
                date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
                medecin_id = medecins[selection[0]][0]
                
                # Obtenir les créneaux définis par le médecin
                heures_medecin_disponibles = self.obtenir_creneaux_definis_medecin(medecin_id, date_str)
                
                # Obtenir les créneaux occupés pour cette date et ce médecin
                heures_occupees = self.obtenir_creneaux_occupes(medecin_id, date_str)
                
                # Filtrer les créneaux occupés
                heures_disponibles = [h for h in heures_medecin_disponibles if h not in heures_occupees]
                
                # Mettre à jour la combobox
                combo_heure['values'] = heures_disponibles
                if heures_disponibles:
                    combo_heure.set(heures_disponibles[0])
                else:
                    combo_heure.set("")
                    
            except (ValueError, IndexError):
                pass
        
        # Lier les événements pour mettre à jour les heures
        combo_jour.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        combo_mois.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        combo_annee.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        listbox.bind('<<ListboxSelect>>', mettre_a_jour_heures)
        
        # Case urgence
        var_urgent = tk.BooleanVar()
        check_urgent = tk.Checkbutton(fenetre_rdv, text="Rendez-vous urgent", variable=var_urgent,
                                     fg="white", bg="#2c2c2c", selectcolor="gray")
        check_urgent.pack(pady=10)
        
        # Bouton confirmer
        def confirmer_rdv():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Erreur", "Veuillez sélectionner un médecin")
                return
            
            # Récupérer les valeurs sélectionnées
            jour = combo_jour.get()
            mois = combo_mois.get()
            annee = combo_annee.get()
            heure_rdv = combo_heure.get()
            
            if not (jour and mois and annee):
                messagebox.showerror("Erreur", "Veuillez sélectionner une date complète")
                return
            
            if not heure_rdv:
                messagebox.showerror("Erreur", "Veuillez sélectionner une heure")
                return
            
            # Construire la date
            date_rdv = f"{int(jour):02d}/{int(mois):02d}/{annee}"
            
            # Valider la date
            date_valide, date_obj_ou_message = self.valider_date(date_rdv)
            if not date_valide:
                messagebox.showerror("Erreur", date_obj_ou_message)
                return
            
            # Valider l'heure
            heure_valide, message_heure = self.valider_heure(heure_rdv)
            if not heure_valide:
                messagebox.showerror("Erreur", message_heure)
                return
            
            # Vérifier que le créneau n'est pas occupé
            medecin_id = medecins[selection[0]][0]
            heures_occupees = self.obtenir_creneaux_occupes(medecin_id, date_rdv)
            
            if heure_rdv in heures_occupees:
                messagebox.showerror("Erreur", "Ce créneau est déjà occupé")
                return
            
            # Vérifier anticipation minimale (30 minutes)
            try:
                datetime_rdv = datetime.combine(date_obj_ou_message, datetime.strptime(heure_rdv, "%H:%M").time())
                if datetime_rdv <= datetime.now() + timedelta(minutes=30):
                    messagebox.showerror("Erreur", "Le rendez-vous doit être programmé au moins 30 minutes à l'avance")
                    return
            except Exception:
                messagebox.showerror("Erreur", "Erreur de validation date/heure")
                return
            
            urgent = 1 if var_urgent.get() else 0
            
            try:
                self.cursor.execute('''
                    INSERT INTO rendez_vous (patient_id, medecin_id, date_rdv, heure_rdv, urgent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (self.patient_connecte['id'], medecin_id, date_rdv, heure_rdv, urgent))
                self.conn.commit()
                messagebox.showinfo("Succès", "Rendez-vous confirmé !")
                fenetre_rdv.destroy()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement: {str(e)}")
        
        btn_confirmer = tk.Button(fenetre_rdv, text="Confirmer rendez-vous", 
                                 command=confirmer_rdv, bg="white", font=("Arial", 10))
        btn_confirmer.pack(pady=10)
    
    def voir_mes_rendez_vous(self):
        # Récupérer les rendez-vous du patient avec l'ID
        self.cursor.execute('''
            SELECT rv.id, rv.date_rdv, rv.heure_rdv, m.nom_complet, m.specialite, rv.urgent, rv.statut, rv.medecin_id
            FROM rendez_vous rv
            JOIN medecins m ON rv.medecin_id = m.id
            WHERE rv.patient_id = ?
            ORDER BY rv.date_rdv, rv.heure_rdv
        ''', (self.patient_connecte['id'],))
        
        rendez_vous = self.cursor.fetchall()
        
        # Fenêtre d'affichage
        fenetre_rdv = tk.Toplevel(self.root)
        fenetre_rdv.title("Mes rendez-vous")
        fenetre_rdv.geometry("700x500")
        fenetre_rdv.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_rdv, text="Mes rendez-vous", font=("Arial", 14, "bold"), 
                fg="white", bg="#2c2c2c").pack(pady=10)
        
        if not rendez_vous:
            tk.Label(fenetre_rdv, text="Aucun rendez-vous programmé", 
                    fg="white", bg="#2c2c2c").pack(pady=50)
        else:
            # Frame pour le treeview
            frame_tree = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Treeview pour afficher les rendez-vous
            columns = ("Date", "Heure", "Médecin", "Spécialité", "Urgent", "Statut")
            tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, anchor="center")
            
            for rdv in rendez_vous:
                urgent_text = "OUI" if rdv[5] else "NON"
                # Stocker l'ID du rendez-vous dans les tags pour pouvoir le récupérer
                item_id = tree.insert("", tk.END, values=(rdv[1], rdv[2], f"Dr. {rdv[3]}", rdv[4], urgent_text, rdv[6]), 
                                    tags=(rdv[0],))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Frame pour les boutons d'action
            frame_actions = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_actions.pack(pady=10)
            
            # Fonction pour annuler un rendez-vous
            def annuler_rdv():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous")
                    return
                
                # Récupérer l'ID du rendez-vous depuis les tags
                rdv_id = tree.item(selection[0])['tags'][0]
                rdv_values = tree.item(selection[0])['values']
                
                # Vérifier que le rendez-vous n'est pas déjà annulé
                if rdv_values[5] == 'annulé':
                    messagebox.showwarning("Attention", "Ce rendez-vous est déjà annulé")
                    return
                
                # Demander confirmation
                if messagebox.askyesno("Confirmation", 
                                     f"Êtes-vous sûr de vouloir annuler le rendez-vous du {rdv_values[0]} à {rdv_values[1]} avec {rdv_values[2]} ?"):
                    try:
                        self.cursor.execute("UPDATE rendez_vous SET statut = 'annulé' WHERE id = ?", (rdv_id,))
                        self.conn.commit()
                        messagebox.showinfo("Succès", "Rendez-vous annulé avec succès")
                        fenetre_rdv.destroy()
                        # Relancer la fenêtre pour voir la mise à jour
                        self.voir_mes_rendez_vous()
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de l'annulation: {str(e)}")
            
            # Fonction pour modifier un rendez-vous
            def modifier_rdv():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous")
                    return
                
                # Récupérer les informations du rendez-vous
                rdv_id = tree.item(selection[0])['tags'][0]
                rdv_values = tree.item(selection[0])['values']
                
                # Vérifier que le rendez-vous n'est pas annulé
                if rdv_values[5] == 'annulé':
                    messagebox.showwarning("Attention", "Impossible de modifier un rendez-vous annulé")
                    return
                
                # Récupérer les détails complets du rendez-vous
                self.cursor.execute('''
                    SELECT medecin_id, date_rdv, heure_rdv, urgent 
                    FROM rendez_vous 
                    WHERE id = ?
                ''', (rdv_id,))
                rdv_details = self.cursor.fetchone()
                
                if rdv_details:
                    self.modifier_rendez_vous(rdv_id, rdv_details[0], rdv_details[1], rdv_details[2], rdv_details[3])
                    fenetre_rdv.destroy()
            
            # Boutons d'action
            btn_modifier = tk.Button(frame_actions, text="Modifier", 
                                   command=modifier_rdv, bg="lightblue", font=("Arial", 10))
            btn_modifier.pack(side=tk.LEFT, padx=10)
            
            btn_annuler = tk.Button(frame_actions, text="Annuler", 
                                  command=annuler_rdv, bg="lightcoral", font=("Arial", 10))
            btn_annuler.pack(side=tk.LEFT, padx=10)
            
            # Note explicative
            tk.Label(fenetre_rdv, text="Sélectionnez un rendez-vous puis cliquez sur 'Modifier' ou 'Annuler'", 
                    font=("Arial", 9), fg="lightgray", bg="#2c2c2c").pack(pady=5)
    
    def modifier_rendez_vous(self, rdv_id, medecin_id_actuel, date_actuelle, heure_actuelle, urgent_actuel):
        """Interface de modification d'un rendez-vous existant"""
        
        # Récupérer la liste des médecins
        self.cursor.execute("SELECT id, nom_complet, specialite FROM medecins")
        medecins = self.cursor.fetchall()
        
        if not medecins:
            messagebox.showwarning("Attention", "Aucun médecin disponible")
            return
        
        # Fenêtre de modification
        fenetre_modif = tk.Toplevel(self.root)
        fenetre_modif.title("Modifier le rendez-vous")
        fenetre_modif.geometry("500x450")
        fenetre_modif.configure(bg="#2c2c2c")
        
        # Titre
        tk.Label(fenetre_modif, text="Modifier le rendez-vous", font=("Arial", 14, "bold"),
                fg="white", bg="#2c2c2c").pack(pady=10)
        
        # Informations actuelles
        info_frame = tk.Frame(fenetre_modif, bg="#2c2c2c")
        info_frame.pack(pady=10)
        
        tk.Label(info_frame, text=f"Rendez-vous actuel : {date_actuelle} à {heure_actuelle}", 
                font=("Arial", 10, "italic"), fg="lightgray", bg="#2c2c2c").pack()
        
        # Liste des médecins
        tk.Label(fenetre_modif, text="Médecin:", font=("Arial", 12, "bold"), 
                fg="white", bg="#2c2c2c").pack(pady=(20,5))
        
        frame_liste = tk.Frame(fenetre_modif, bg="#2c2c2c")
        frame_liste.pack(pady=10)
        
        listbox = tk.Listbox(frame_liste, font=("Arial", 10), width=50, height=6)
        for i, medecin in enumerate(medecins):
            listbox.insert(tk.END, f"Dr. {medecin[1]} - {medecin[2]}")
            # Présélectionner le médecin actuel
            if medecin[0] == medecin_id_actuel:
                listbox.selection_set(i)
        listbox.pack()
        
        # Sélection date
        frame_date = tk.Frame(fenetre_modif, bg="#2c2c2c")
        frame_date.pack(pady=10)
        
        tk.Label(frame_date, text="Nouvelle date:", fg="white", bg="#2c2c2c", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Sélecteurs pour jour, mois, année avec valeurs actuelles
        aujourd_hui = datetime.now()
        date_parts = date_actuelle.split('/')
        jour_actuel = int(date_parts[0])
        mois_actuel = int(date_parts[1])
        annee_actuelle = int(date_parts[2])
        
        # Jour (1-31)
        combo_jour = ttk.Combobox(frame_date, width=3, state="readonly")
        combo_jour['values'] = tuple(range(1, 32))
        combo_jour.set(jour_actuel)
        combo_jour.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Mois (1-12)
        combo_mois = ttk.Combobox(frame_date, width=3, state="readonly")
        combo_mois['values'] = tuple(range(1, 13))
        combo_mois.set(mois_actuel)
        combo_mois.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Année (année actuelle + 1)
        combo_annee = ttk.Combobox(frame_date, width=5, state="readonly")
        combo_annee['values'] = tuple(range(aujourd_hui.year, aujourd_hui.year + 2))
        combo_annee.set(annee_actuelle)
        combo_annee.pack(side=tk.LEFT, padx=2)
        
        # Sélection heure
        frame_heure = tk.Frame(fenetre_modif, bg="#2c2c2c")
        frame_heure.pack(pady=10)
        
        tk.Label(frame_heure, text="Nouvelle heure:", fg="white", bg="#2c2c2c", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=5)
        
        # Combobox pour les heures disponibles
        combo_heure = ttk.Combobox(frame_heure, width=8, state="readonly")
        heures_initiales = self.generer_heures_disponibles()
        combo_heure['values'] = heures_initiales
        combo_heure.set(heure_actuelle)  # Définir l'heure actuelle
        combo_heure.pack(side=tk.LEFT, padx=5)
        
        # Fonction pour mettre à jour les heures disponibles
        def mettre_a_jour_heures(*args):
            try:
                selection = listbox.curselection()
                if not selection:
                    return
                
                jour = combo_jour.get()
                mois = combo_mois.get()
                annee = combo_annee.get()
                
                if not (jour and mois and annee):
                    return
                
                date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
                nouveau_medecin_id = medecins[selection[0]][0]
                
                # Obtenir les créneaux définis par le médecin
                heures_medecin_disponibles = self.obtenir_creneaux_definis_medecin(nouveau_medecin_id, date_str)
                
                # Obtenir les créneaux occupés pour cette date et ce médecin
                heures_occupees = self.obtenir_creneaux_occupes(nouveau_medecin_id, date_str)
                
                # Si on reste sur le même médecin et la même date, permettre de garder l'heure actuelle
                if nouveau_medecin_id == medecin_id_actuel and date_str == date_actuelle:
                    # Retirer l'heure actuelle des heures occupées pour permettre sa modification
                    if heure_actuelle in heures_occupees:
                        heures_occupees.remove(heure_actuelle)
                
                # Filtrer les créneaux occupés
                heures_disponibles = [h for h in heures_medecin_disponibles if h not in heures_occupees]
                
                # Mettre à jour la combobox
                combo_heure['values'] = heures_disponibles
                if heure_actuelle in heures_disponibles:
                    combo_heure.set(heure_actuelle)
                elif heures_disponibles:
                    combo_heure.set(heures_disponibles[0])
                else:
                    combo_heure.set("")
                    
            except (ValueError, IndexError):
                pass
        
        # Lier les événements
        combo_jour.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        combo_mois.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        combo_annee.bind('<<ComboboxSelected>>', mettre_a_jour_heures)
        listbox.bind('<<ListboxSelect>>', mettre_a_jour_heures)
        
        # Mettre à jour une première fois pour charger les bonnes heures
        mettre_a_jour_heures()
        
        # Case urgence
        var_urgent = tk.BooleanVar()
        var_urgent.set(urgent_actuel)  # Définir la valeur actuelle
        check_urgent = tk.Checkbutton(fenetre_modif, text="Rendez-vous urgent", variable=var_urgent,
                                     fg="white", bg="#2c2c2c", selectcolor="gray")
        check_urgent.pack(pady=10)
        
        # Boutons d'action
        frame_boutons = tk.Frame(fenetre_modif, bg="#2c2c2c")
        frame_boutons.pack(pady=20)
        
        def confirmer_modification():
            selection = listbox.curselection()
            if not selection:
                messagebox.showerror("Erreur", "Veuillez sélectionner un médecin")
                return
            
            # Récupérer les nouvelles valeurs
            jour = combo_jour.get()
            mois = combo_mois.get()
            annee = combo_annee.get()
            nouvelle_heure = combo_heure.get()
            
            if not (jour and mois and annee):
                messagebox.showerror("Erreur", "Veuillez sélectionner une date complète")
                return
            
            if not nouvelle_heure:
                messagebox.showerror("Erreur", "Veuillez sélectionner une heure")
                return
            
            # Construire la nouvelle date
            nouvelle_date = f"{int(jour):02d}/{int(mois):02d}/{annee}"
            nouveau_medecin_id = medecins[selection[0]][0]
            
            # Valider la nouvelle date
            date_valide, date_obj_ou_message = self.valider_date(nouvelle_date)
            if not date_valide:
                messagebox.showerror("Erreur", date_obj_ou_message)
                return
            
            # Valider l'heure
            heure_valide, message_heure = self.valider_heure(nouvelle_heure)
            if not heure_valide:
                messagebox.showerror("Erreur", message_heure)
                return
            
            # Vérifier que le créneau n'est pas occupé
            heures_occupees = self.obtenir_creneaux_occupes(nouveau_medecin_id, nouvelle_date)
            
            # Si même médecin et même date, permettre de garder la même heure
            if not (nouveau_medecin_id == medecin_id_actuel and nouvelle_date == date_actuelle and nouvelle_heure == heure_actuelle):
                if nouvelle_heure in heures_occupees:
                    messagebox.showerror("Erreur", "Ce créneau est déjà occupé")
                    return
            
            # Vérifier anticipation minimale (30 minutes)
            try:
                datetime_rdv = datetime.combine(date_obj_ou_message, datetime.strptime(nouvelle_heure, "%H:%M").time())
                if datetime_rdv <= datetime.now() + timedelta(minutes=30):
                    messagebox.showerror("Erreur", "Le rendez-vous doit être programmé au moins 30 minutes à l'avance")
                    return
            except Exception:
                messagebox.showerror("Erreur", "Erreur de validation date/heure")
                return
            
            urgent = 1 if var_urgent.get() else 0
            
            try:
                # Mettre à jour le rendez-vous
                self.cursor.execute('''
                    UPDATE rendez_vous 
                    SET medecin_id = ?, date_rdv = ?, heure_rdv = ?, urgent = ?
                    WHERE id = ?
                ''', (nouveau_medecin_id, nouvelle_date, nouvelle_heure, urgent, rdv_id))
                self.conn.commit()
                messagebox.showinfo("Succès", "Rendez-vous modifié avec succès !")
                fenetre_modif.destroy()
                # Relancer la fenêtre des rendez-vous pour voir la mise à jour
                self.voir_mes_rendez_vous()
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la modification: {str(e)}")
        
        btn_confirmer = tk.Button(frame_boutons, text="Confirmer modification", 
                                 command=confirmer_modification, bg="lightgreen", font=("Arial", 10))
        btn_confirmer.pack(side=tk.LEFT, padx=10)
        
        btn_annuler = tk.Button(frame_boutons, text="Annuler", 
                               command=fenetre_modif.destroy, bg="lightgray", font=("Arial", 10))
        btn_annuler.pack(side=tk.LEFT, padx=10)
    
    def deconnexion(self):
        self.patient_connecte = None
        self.creer_interface_connexion()
    
    def quitter(self):
        self.conn.close()
        self.root.quit()
        self.root.destroy()

root = tk.Tk()
app = EspacePatient(root)
root.mainloop()