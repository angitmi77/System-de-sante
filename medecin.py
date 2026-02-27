import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta
import calendar

class EspaceMedecin:
    def __init__(self, root):
        self.root = root
        self.root.title("Espace Médecin")
        self.root.geometry("900x700")
        self.root.configure(bg="#2c2c2c")
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        # Initialiser la base de données
        self.init_database()
        
        # Médecin connecté
        self.medecin_connecte = None
        
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
        
        # Créer la table des créneaux si elle n'existe pas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS creneaux_disponibles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medecin_id INTEGER,
                date_creneau TEXT NOT NULL,
                heure_debut TEXT NOT NULL,
                heure_fin TEXT NOT NULL,
                disponible INTEGER DEFAULT 1,
                FOREIGN KEY (medecin_id) REFERENCES medecins (id)
            )
        ''')
        self.conn.commit()
    
    def creer_interface_connexion(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Connexion Médecin",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c2c2c"
        )
        titre.pack(pady=50)
        
        # Frame pour le formulaire
        frame_form = tk.Frame(self.root, bg="#2c2c2c")
        frame_form.pack(expand=True)
        
        # Style des labels
        style_label = {
            "font": ("Arial", 12),
            "fg": "white",
            "bg": "#2c2c2c"
        }
        
        # Champ Nom d'utilisateur
        tk.Label(frame_form, text="Nom d'utilisateur:", **style_label).grid(row=0, column=0, sticky="w", pady=10, padx=20)
        self.entry_username = tk.Entry(frame_form, font=("Arial", 12), width=25)
        self.entry_username.grid(row=0, column=1, pady=10, padx=20)
        
        # Champ Mot de passe
        tk.Label(frame_form, text="Mot de passe:", **style_label).grid(row=1, column=0, sticky="w", pady=10, padx=20)
        self.entry_password = tk.Entry(frame_form, font=("Arial", 12), width=25, show="*")
        self.entry_password.grid(row=1, column=1, pady=10, padx=20)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.root, bg="#2c2c2c")
        frame_boutons.pack(pady=30)
        
        # Bouton Se connecter
        btn_connexion = tk.Button(
            frame_boutons,
            text="Se connecter",
            command=self.connexion_medecin,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_connexion.pack(side=tk.LEFT, padx=10)
        
        # Bouton Quitter
        btn_quitter = tk.Button(
            frame_boutons,
            text="Quitter",
            command=self.quitter,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_quitter.pack(side=tk.LEFT, padx=10)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.connexion_medecin())
    
    def connexion_medecin(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        self.cursor.execute('''
            SELECT id, nom_complet, specialite FROM medecins 
            WHERE nom_utilisateur = ? AND mot_de_passe = ?
        ''', (username, password))
        
        medecin = self.cursor.fetchone()
        if medecin:
            self.medecin_connecte = {
                "id": medecin[0], 
                "nom": medecin[1], 
                "specialite": medecin[2]
            }
            messagebox.showinfo("Succès", f"Bienvenue Dr. {medecin[1]} !")
            self.menu_medecin()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
    
    def menu_medecin(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text=f"Dr. {self.medecin_connecte['nom']} - {self.medecin_connecte['specialite']}",
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
        
        # Bouton Voir mes rendez-vous
        btn_rdv = tk.Button(
            frame_boutons,
            text="Voir mes rendez-vous",
            command=self.voir_mes_rendez_vous,
            **style_bouton
        )
        btn_rdv.pack(pady=10)
        
        # Bouton Gérer mes créneaux
        btn_creneaux = tk.Button(
            frame_boutons,
            text="Gérer mes créneaux",
            command=self.gerer_creneaux,
            **style_bouton
        )
        btn_creneaux.pack(pady=10)
        
        # Bouton Rendez-vous urgents
        btn_urgents = tk.Button(
            frame_boutons,
            text="Rendez-vous urgents",
            command=self.voir_rdv_urgents,
            **style_bouton
        )
        btn_urgents.pack(pady=10)
        
        # Bouton Déconnexion
        btn_deconnexion = tk.Button(
            frame_boutons,
            text="Déconnexion",
            command=self.deconnexion,
            **style_bouton
        )
        btn_deconnexion.pack(pady=10)
    
    def voir_mes_rendez_vous(self):
        # Récupérer les rendez-vous du médecin
        self.cursor.execute('''
            SELECT rv.date_rdv, rv.heure_rdv, p.nom_complet, p.telephone, p.age, p.adresse, rv.urgent, rv.statut, rv.id
            FROM rendez_vous rv
            JOIN patients p ON rv.patient_id = p.id
            WHERE rv.medecin_id = ?
            ORDER BY rv.date_rdv, rv.heure_rdv
        ''', (self.medecin_connecte['id'],))
        
        rendez_vous = self.cursor.fetchall()
        
        # Créer fenêtre d'affichage
        fenetre_rdv = tk.Toplevel(self.root)
        fenetre_rdv.title("Mes rendez-vous")
        fenetre_rdv.geometry("700x500")
        fenetre_rdv.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_rdv, text="Mes rendez-vous programmés", 
                font=("Arial", 14, "bold"), fg="white", bg="#2c2c2c").pack(pady=10)
        
        if not rendez_vous:
            tk.Label(fenetre_rdv, text="Aucun rendez-vous programmé", 
                    fg="white", bg="#2c2c2c").pack(pady=50)
        else:
            # Frame avec scrollbar
            frame_tree = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Treeview pour afficher les rendez-vous avec informations complètes
            columns = ("Date", "Heure", "Patient", "Téléphone", "Âge", "Adresse", "Urgent", "Statut")
            tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=12)
            
            # Configurer les colonnes avec des largeurs adaptées
            tree.heading("Date", text="Date")
            tree.column("Date", width=80, anchor="center")
            tree.heading("Heure", text="Heure")
            tree.column("Heure", width=60, anchor="center")
            tree.heading("Patient", text="Patient")
            tree.column("Patient", width=120, anchor="center")
            tree.heading("Téléphone", text="Téléphone")
            tree.column("Téléphone", width=100, anchor="center")
            tree.heading("Âge", text="Âge")
            tree.column("Âge", width=40, anchor="center")
            tree.heading("Adresse", text="Adresse")
            tree.column("Adresse", width=150, anchor="w")
            tree.heading("Urgent", text="Urgent")
            tree.column("Urgent", width=60, anchor="center")
            tree.heading("Statut", text="Statut")
            tree.column("Statut", width=80, anchor="center")
            
            # Colorer les lignes urgentes
            tree.tag_configure("urgent", background="lightcoral")
            tree.tag_configure("normal", background="lightgray")
            
            for rdv in rendez_vous:
                urgent_text = "OUI" if rdv[6] else "NON"
                tag = "urgent" if rdv[6] else "normal"
                telephone = rdv[3] if rdv[3] else "N/A"
                age = rdv[4] if rdv[4] else "N/A"
                adresse = rdv[5] if rdv[5] else "N/A"
                tree.insert("", tk.END, values=(rdv[0], rdv[1], rdv[2], telephone, age, adresse, urgent_text, rdv[7]), 
                           tags=(tag,))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Frame pour les boutons d'action
            frame_actions = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_actions.pack(pady=10)
            
            def annuler_rdv():
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous")
                    return
                
                # Récupérer l'ID du rendez-vous sélectionné
                item = tree.item(selection[0])
                values = item['values']
                
                # Trouver le rendez-vous correspondant (mise à jour des indices)
                for rdv in rendez_vous:
                    if rdv[0] == values[0] and rdv[1] == values[1] and rdv[2] == values[2]:
                        if messagebox.askyesno("Confirmation", "Annuler ce rendez-vous ?"):
                            self.cursor.execute("UPDATE rendez_vous SET statut = 'annulé' WHERE id = ?", (rdv[8],))
                            self.conn.commit()
                            messagebox.showinfo("Succès", "Rendez-vous annulé")
                            fenetre_rdv.destroy()
                            self.voir_mes_rendez_vous()
                        break
            
            btn_annuler = tk.Button(frame_actions, text="Annuler RDV sélectionné", 
                                   command=annuler_rdv, bg="lightcoral", font=("Arial", 10))
            btn_annuler.pack(side=tk.LEFT, padx=10)
    
    def gerer_creneaux(self):
        # Fenêtre de gestion des créneaux
        fenetre_creneaux = tk.Toplevel(self.root)
        fenetre_creneaux.title("Gérer mes créneaux")
        fenetre_creneaux.geometry("600x600")
        fenetre_creneaux.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_creneaux, text="Gestion des créneaux disponibles", 
                font=("Arial", 14, "bold"), fg="white", bg="#2c2c2c").pack(pady=10)
        
        # Frame pour la sélection de date (même que dans patient.py)
        frame_date = tk.Frame(fenetre_creneaux, bg="#2c2c2c")
        frame_date.pack(pady=10)
        
        tk.Label(frame_date, text="Date:", fg="white", bg="#2c2c2c", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # Sélecteurs pour jour, mois, année (limités aux dates futures)
        aujourd_hui = datetime.now()
        
        # Jour (limité selon le mois et l'année sélectionnés)
        combo_jour = ttk.Combobox(frame_date, width=3, state="readonly")
        # Initialiser avec les jours valides pour aujourd'hui
        if aujourd_hui.month == aujourd_hui.month:  # Mois actuel
            jours_valides = list(range(aujourd_hui.day, 32))
        else:
            jours_valides = list(range(1, 32))
        combo_jour['values'] = tuple(jours_valides)
        combo_jour.set(aujourd_hui.day)
        combo_jour.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Mois (à partir du mois actuel)
        combo_mois = ttk.Combobox(frame_date, width=3, state="readonly")
        mois_valides = list(range(aujourd_hui.month, 13))
        combo_mois['values'] = tuple(mois_valides)
        combo_mois.set(aujourd_hui.month)
        combo_mois.pack(side=tk.LEFT, padx=2)
        
        tk.Label(frame_date, text="/", fg="white", bg="#2c2c2c").pack(side=tk.LEFT)
        
        # Année (année actuelle + 1)
        combo_annee = ttk.Combobox(frame_date, width=5, state="readonly")
        combo_annee['values'] = tuple(range(aujourd_hui.year, aujourd_hui.year + 2))
        combo_annee.set(aujourd_hui.year)
        combo_annee.pack(side=tk.LEFT, padx=2)
        
        # Fonction pour mettre à jour les jours disponibles selon le mois/année
        def mettre_a_jour_jours(*args):
            try:
                mois_sel = int(combo_mois.get())
                annee_sel = int(combo_annee.get())
                
                # Si c'est l'année et le mois actuels, commencer par aujourd'hui
                if annee_sel == aujourd_hui.year and mois_sel == aujourd_hui.month:
                    jour_min = aujourd_hui.day
                else:
                    jour_min = 1
                
                # Déterminer le nombre de jours dans le mois
                import calendar as cal
                _, jours_dans_mois = cal.monthrange(annee_sel, mois_sel)
                
                jours_valides = list(range(jour_min, jours_dans_mois + 1))
                combo_jour['values'] = tuple(jours_valides)
                
                # Ajuster la sélection si nécessaire
                jour_actuel = combo_jour.get()
                if jour_actuel and int(jour_actuel) < jour_min:
                    combo_jour.set(jour_min)
                elif not jour_actuel or int(jour_actuel) > jours_dans_mois:
                    combo_jour.set(jours_valides[0] if jours_valides else jour_min)
                    
            except (ValueError, IndexError):
                pass
        
        # Fonction pour mettre à jour les mois disponibles selon l'année
        def mettre_a_jour_mois(*args):
            try:
                annee_sel = int(combo_annee.get())
                
                # Si c'est l'année actuelle, commencer par le mois actuel
                if annee_sel == aujourd_hui.year:
                    mois_min = aujourd_hui.month
                    mois_valides = list(range(mois_min, 13))
                else:
                    mois_valides = list(range(1, 13))
                
                combo_mois['values'] = tuple(mois_valides)
                
                # Ajuster la sélection si nécessaire
                mois_actuel = combo_mois.get()
                if mois_actuel and int(mois_actuel) < mois_valides[0]:
                    combo_mois.set(mois_valides[0])
                elif not mois_actuel or int(mois_actuel) > 12:
                    combo_mois.set(mois_valides[0])
                    
                # Mettre à jour les jours aussi
                mettre_a_jour_jours()
                    
            except (ValueError, IndexError):
                pass
        
        # Lier les événements
        combo_annee.bind('<<ComboboxSelected>>', mettre_a_jour_mois)
        combo_mois.bind('<<ComboboxSelected>>', mettre_a_jour_jours)
        
        # Sélection créneaux (heure début et heure fin)
        frame_creneaux = tk.Frame(fenetre_creneaux, bg="#2c2c2c")
        frame_creneaux.pack(pady=10)
        
        tk.Label(frame_creneaux, text="Heure début:", fg="white", bg="#2c2c2c", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # Combobox pour l'heure de début
        combo_heure_debut = ttk.Combobox(frame_creneaux, width=8, state="readonly")
        tous_creneaux = self.generer_tous_creneaux_possibles()
        combo_heure_debut['values'] = tous_creneaux
        if tous_creneaux:
            combo_heure_debut.set(tous_creneaux[0])
        combo_heure_debut.pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame_creneaux, text="Heure fin:", fg="white", bg="#2c2c2c", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # Combobox pour l'heure de fin
        combo_heure_fin = ttk.Combobox(frame_creneaux, width=8, state="readonly")
        combo_heure_fin['values'] = tous_creneaux
        if len(tous_creneaux) > 1:
            combo_heure_fin.set(tous_creneaux[1])  # Par défaut, 30 min plus tard
        combo_heure_fin.pack(side=tk.LEFT, padx=5)
        
        # Fonction pour mettre à jour l'affichage selon la date sélectionnée
        def mettre_a_jour_affichage(*args):
            try:
                jour = combo_jour.get()
                mois = combo_mois.get()
                annee = combo_annee.get()
                
                if jour and mois and annee:
                    date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
                    afficher_creneaux_jour(date_str)
                    
            except (ValueError, IndexError):
                pass
        
        # Lier les événements
        combo_jour.bind('<<ComboboxSelected>>', mettre_a_jour_affichage)
        combo_mois.bind('<<ComboboxSelected>>', mettre_a_jour_affichage)
        combo_annee.bind('<<ComboboxSelected>>', mettre_a_jour_affichage)
        
        # Frame pour les actions
        frame_actions = tk.Frame(fenetre_creneaux, bg="#2c2c2c")
        frame_actions.pack(pady=10)
        
        def ajouter_creneau():
            jour = combo_jour.get()
            mois = combo_mois.get()
            annee = combo_annee.get()
            heure_debut = combo_heure_debut.get()
            heure_fin = combo_heure_fin.get()
            
            if not all([jour, mois, annee, heure_debut, heure_fin]):
                messagebox.showerror("Erreur", "Veuillez sélectionner une date, une heure de début et une heure de fin")
                return
            
            # Vérifier que l'heure de fin est après l'heure de début
            try:
                debut = datetime.strptime(heure_debut, "%H:%M")
                fin = datetime.strptime(heure_fin, "%H:%M")
                
                if fin <= debut:
                    messagebox.showerror("Erreur", "L'heure de fin doit être après l'heure de début")
                    return
                    
            except ValueError:
                messagebox.showerror("Erreur", "Format d'heure invalide")
                return
            
            date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
            
            # Vérifier que la date n'est pas dans le passé
            try:
                date_creneau = datetime(int(annee), int(mois), int(jour)).date()
                date_aujourd_hui = datetime.now().date()
                
                if date_creneau < date_aujourd_hui:
                    messagebox.showerror("Erreur", "Impossible de créer un créneau dans le passé")
                    return
                
                # Si c'est aujourd'hui, vérifier que l'heure de début est dans le futur
                if date_creneau == date_aujourd_hui:
                    maintenant = datetime.now()
                    datetime_debut = datetime.combine(date_creneau, debut.time())
                    
                    if datetime_debut <= maintenant:
                        messagebox.showerror("Erreur", "L'heure de début doit être dans le futur pour aujourd'hui")
                        return
                    
            except ValueError:
                messagebox.showerror("Erreur", "Date invalide")
                return
            
            try:
                # Vérifier si le créneau existe déjà
                self.cursor.execute('''
                    SELECT id FROM creneaux_disponibles
                    WHERE medecin_id = ? AND date_creneau = ? AND heure_debut = ? AND heure_fin = ?
                ''', (self.medecin_connecte['id'], date_str, heure_debut, heure_fin))
                
                if self.cursor.fetchone():
                    messagebox.showwarning("Attention", "Ce créneau existe déjà")
                    return
                
                # Ajouter le créneau
                self.cursor.execute('''
                    INSERT INTO creneaux_disponibles (medecin_id, date_creneau, heure_debut, heure_fin)
                    VALUES (?, ?, ?, ?)
                ''', (self.medecin_connecte['id'], date_str, heure_debut, heure_fin))
                self.conn.commit()
                
                messagebox.showinfo("Succès", f"Créneau {heure_debut}-{heure_fin} ajouté pour le {date_str}")
                afficher_creneaux_jour(date_str)
                
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {str(e)}")
        
        btn_ajouter = tk.Button(frame_actions, text="Ajouter créneau", command=ajouter_creneau,
                               bg="lightgreen", font=("Arial", 12), width=15)
        btn_ajouter.pack(side=tk.LEFT, padx=10)
        
        def actualiser():
            jour = combo_jour.get()
            mois = combo_mois.get()
            annee = combo_annee.get()
            
            if jour and mois and annee:
                date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
                afficher_creneaux_jour(date_str)
        
        btn_actualiser = tk.Button(frame_actions, text="Actualiser", command=actualiser,
                                  bg="lightblue", font=("Arial", 12), width=15)
        btn_actualiser.pack(side=tk.LEFT, padx=10)
        
        # Liste des créneaux existants pour le jour sélectionné
        frame_liste = tk.Frame(fenetre_creneaux, bg="#2c2c2c")
        frame_liste.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(frame_liste, text="Créneaux du jour sélectionné:", 
                font=("Arial", 12, "bold"), fg="white", bg="#2c2c2c").pack()
        
        # Treeview pour afficher les créneaux  
        columns = ("Heure",)
        tree = ttk.Treeview(frame_liste, columns=columns, show="headings", height=12)
        
        tree.heading("Heure", text="Créneau (Début - Fin)")
        tree.column("Heure", width=250, anchor="center")
        
        tree.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame pour les boutons d'action sur les créneaux
        frame_btn = tk.Frame(frame_liste, bg="#2c2c2c")
        frame_btn.pack(pady=5)
        
        def supprimer_creneau():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Attention", "Veuillez sélectionner un créneau")
                return
            
            jour = combo_jour.get()
            mois = combo_mois.get()
            annee = combo_annee.get()
            
            if not all([jour, mois, annee]):
                return
            
            date_str = f"{int(jour):02d}/{int(mois):02d}/{annee}"
            
            item = tree.item(selection[0])
            creneau_complet = item['values'][0]  # Format "08:00 - 08:30"
            
            # Extraire les heures de début et fin
            try:
                parties = creneau_complet.split(' - ')
                heure_debut = parties[0].strip()
                heure_fin = parties[1].strip()
            except:
                messagebox.showerror("Erreur", "Format de créneau invalide")
                return
            
            if messagebox.askyesno("Confirmation", f"Supprimer le créneau {creneau_complet} ?"):
                self.cursor.execute('''
                    DELETE FROM creneaux_disponibles
                    WHERE medecin_id = ? AND date_creneau = ? AND heure_debut = ? AND heure_fin = ?
                ''', (self.medecin_connecte['id'], date_str, heure_debut, heure_fin))
                self.conn.commit()
                messagebox.showinfo("Succès", "Créneau supprimé")
                afficher_creneaux_jour(date_str)
        
        btn_supprimer = tk.Button(frame_btn, text="Supprimer", command=supprimer_creneau,
                                 bg="lightcoral", font=("Arial", 10))
        btn_supprimer.pack(side=tk.LEFT, padx=5)
        
        def afficher_creneaux_jour(date_str):
            # Vider la liste
            for item in tree.get_children():
                tree.delete(item)
            
            # Récupérer les créneaux du jour
            self.cursor.execute('''
                SELECT heure_debut, heure_fin, disponible
                FROM creneaux_disponibles
                WHERE medecin_id = ? AND date_creneau = ?
                ORDER BY heure_debut
            ''', (self.medecin_connecte['id'], date_str))
            
            creneaux = self.cursor.fetchall()
            
            for creneau in creneaux:
                heure_affichage = f"{creneau[0]} - {creneau[1]}"
                # Tous les créneaux créés sont disponibles par défaut
                tree.insert("", tk.END, values=(heure_affichage,), tags=("creneau",))
            
            # Configurer la couleur des créneaux
            tree.tag_configure("creneau", background="lightgreen")
        
        # Affichage initial
        date_initiale = f"{aujourd_hui.day:02d}/{aujourd_hui.month:02d}/{aujourd_hui.year}"
        afficher_creneaux_jour(date_initiale)
    
    def generer_tous_creneaux_possibles(self):
        """Générer tous les créneaux possibles (8h-16h30, créneaux 30min)"""
        heures_possibles = []
        
        # Matin : 8h00 à 11h30
        for heure in range(8, 12):
            for minute in [0, 30]:
                heures_possibles.append(f"{heure:02d}:{minute:02d}")
        
        # Après-midi : 13h00 à 16h30
        for heure in range(13, 17):
            for minute in [0, 30]:
                if heure == 16 and minute > 30:
                    break
                heures_possibles.append(f"{heure:02d}:{minute:02d}")
        
        return heures_possibles
    
    def voir_rdv_urgents(self):
        # Récupérer uniquement les rendez-vous urgents
        self.cursor.execute('''
            SELECT rv.date_rdv, rv.heure_rdv, p.nom_complet, rv.statut
            FROM rendez_vous rv
            JOIN patients p ON rv.patient_id = p.id
            WHERE rv.medecin_id = ? AND rv.urgent = 1
            ORDER BY rv.date_rdv, rv.heure_rdv
        ''', (self.medecin_connecte['id'],))
        
        rdv_urgents = self.cursor.fetchall()
        
        # Fenêtre d'affichage
        fenetre_urgents = tk.Toplevel(self.root)
        fenetre_urgents.title("Rendez-vous urgents")
        fenetre_urgents.geometry("600x400")
        fenetre_urgents.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_urgents, text="⚠️ RENDEZ-VOUS URGENTS ⚠️", 
                font=("Arial", 16, "bold"), fg="red", bg="#2c2c2c").pack(pady=20)
        
        if not rdv_urgents:
            tk.Label(fenetre_urgents, text="Aucun rendez-vous urgent", 
                    fg="white", bg="#2c2c2c", font=("Arial", 12)).pack(pady=50)
        else:
            # Treeview pour les rendez-vous urgents
            columns = ("Date", "Heure", "Patient", "Statut")
            tree = ttk.Treeview(fenetre_urgents, columns=columns, show="headings", height=12)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=130, anchor="center")
            
            # Configurer le style urgent
            tree.tag_configure("urgent", background="lightcoral", foreground="darkred")
            
            for rdv in rdv_urgents:
                tree.insert("", tk.END, values=rdv, tags=("urgent",))
            
            tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Note explicative
            tk.Label(fenetre_urgents, text="Ces patients nécessitent une attention prioritaire", 
                    fg="orange", bg="#2c2c2c", font=("Arial", 10, "italic")).pack(pady=10)
    
    def deconnexion(self):
        self.medecin_connecte = None
        self.creer_interface_connexion()
    
    def quitter(self):
        self.conn.close()
        self.root.quit()
        self.root.destroy()

root = tk.Tk()
app = EspaceMedecin(root)
root.mainloop()