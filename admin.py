import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import re

class EspaceAdministrateur:
    def __init__(self, root):
        self.root = root
        self.root.title("Espace Administrateur")
        self.root.geometry("500x400")
        self.root.configure(bg="#2c2c2c")
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        # Initialiser la base de données
        self.init_database()
        
        # Admin connecté
        self.admin_connecte = False
        
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
            CREATE TABLE IF NOT EXISTS medecins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_complet TEXT NOT NULL,
                specialite TEXT NOT NULL,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_utilisateur TEXT UNIQUE NOT NULL,
                mot_de_passe TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
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
    
    def valider_specialite(self, specialite):
        """Valider la spécialité médicale"""
        specialites_valides = [
            "Radiologue",
            "Anesthésiste réanimateur", 
            "Cardiologue",
            "Dentiste"
        ]
        
        if specialite not in specialites_valides:
            return False, f"Spécialité non valide. Options: {', '.join(specialites_valides)}"
        
        return True, specialite
    
    def valider_formulaire_medecin(self, nom, specialite, username, password):
        """Valider un formulaire médecin complet"""
        erreurs = []
        
        valid_nom, msg_nom = self.valider_nom_complet(nom)
        if not valid_nom:
            erreurs.append(f"Nom: {msg_nom}")
        
        valid_spec, msg_spec = self.valider_specialite(specialite)
        if not valid_spec:
            erreurs.append(f"Spécialité: {msg_spec}")
        
        valid_user, msg_user = self.valider_nom_utilisateur(username)
        if not valid_user:
            erreurs.append(f"Utilisateur: {msg_user}")
        
        valid_pass, msg_pass = self.valider_mot_de_passe(password)
        if not valid_pass:
            erreurs.append(f"Mot de passe: {msg_pass}")
        
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
            text="Connexion Administrateur",
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
            command=self.connexion_admin,
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
        self.root.bind('<Return>', lambda e: self.connexion_admin())
    
    def connexion_admin(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Vérifier les identifiants
        self.cursor.execute('''
            SELECT id FROM admin 
            WHERE nom_utilisateur = ? AND mot_de_passe = ?
        ''', (username, password))
        
        admin = self.cursor.fetchone()
        if admin:
            self.admin_connecte = True
            messagebox.showinfo("Succès", "Connexion administrateur réussie !")
            self.creer_menu_principal()
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect")
    
    def creer_menu_principal(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Espace Administrateur",
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
        
        # Bouton Ajouter un médecin
        btn_ajouter = tk.Button(
            frame_boutons,
            text="Ajouter un médecin",
            command=self.ajouter_medecin,
            **style_bouton
        )
        btn_ajouter.pack(pady=10)
        
        # Bouton Supprimer un médecin
        btn_supprimer = tk.Button(
            frame_boutons,
            text="Supprimer un médecin",
            command=self.supprimer_medecin,
            **style_bouton
        )
        btn_supprimer.pack(pady=10)
        
        # Bouton Voir les médecins
        btn_voir = tk.Button(
            frame_boutons,
            text="Voir les médecins",
            command=self.voir_medecins,
            **style_bouton
        )
        btn_voir.pack(pady=10)
        
        # Bouton Voir tous les rendez-vous
        btn_rdv = tk.Button(
            frame_boutons,
            text="Voir tous les rendez-vous",
            command=self.voir_tous_rendez_vous,
            **style_bouton
        )
        btn_rdv.pack(pady=10)
        
        # Bouton Déconnexion
        btn_deconnexion = tk.Button(
            frame_boutons,
            text="Déconnexion",
            command=self.deconnexion,
            **style_bouton
        )
        btn_deconnexion.pack(pady=10)
        
        # Bouton Quitter
        btn_quitter = tk.Button(
            frame_boutons,
            text="Quitter",
            command=self.quitter,
            **style_bouton
        )
        btn_quitter.pack(pady=10)
    
    def ajouter_medecin(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Ajouter un médecin",
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
        self.entry_nom.grid(row=0, column=1, padx=10, pady=5)
        
        # Champ Spécialité (liste déroulante)
        tk.Label(frame_form, text="Spécialité", **style_label).grid(row=1, column=0, sticky="w", pady=5)
        self.combo_specialite = ttk.Combobox(frame_form, font=("Arial", 10), width=28, state="readonly")
        self.combo_specialite['values'] = (
            "Radiologue",
            "Anesthésiste réanimateur",
            "Cardiologue", 
            "Dentiste"
        )
        self.combo_specialite.grid(row=1, column=1, padx=10, pady=5)
        
        # Champ Nom d'utilisateur
        tk.Label(frame_form, text="Nom d'utilisateur", **style_label).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_username = tk.Entry(frame_form, font=("Arial", 10), width=30)
        self.entry_username.grid(row=2, column=1, padx=10, pady=5)
        
        # Champ Mot de passe
        tk.Label(frame_form, text="Mot de passe", **style_label).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_password = tk.Entry(frame_form, font=("Arial", 10), width=30, show="*")
        self.entry_password.grid(row=3, column=1, padx=10, pady=5)
        
        # Frame pour les boutons
        frame_boutons = tk.Frame(self.root, bg="#2c2c2c")
        frame_boutons.pack(pady=20)
        
        # Bouton Enregistrer
        btn_enregistrer = tk.Button(
            frame_boutons,
            text="Enregistrer",
            command=self.enregistrer_medecin,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_enregistrer.pack(side=tk.LEFT, padx=10)
        
        # Bouton Retour
        btn_retour = tk.Button(
            frame_boutons,
            text="Retour",
            command=self.creer_menu_principal,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_retour.pack(side=tk.LEFT, padx=10)
    
    def enregistrer_medecin(self):
        nom = self.entry_nom.get().strip()
        specialite = self.combo_specialite.get()
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        # Validation avec les méthodes intégrées
        valide, message = self.valider_formulaire_medecin(nom, specialite, username, password)
        
        if not valide:
            messagebox.showerror("Erreur de validation", message)
            return
        
        # Nettoyer les données validées
        _, nom_clean = self.valider_nom_complet(nom)
        _, username_clean = self.valider_nom_utilisateur(username)
        
        try:
            self.cursor.execute('''
                INSERT INTO medecins (nom_complet, specialite, nom_utilisateur, mot_de_passe)
                VALUES (?, ?, ?, ?)
            ''', (nom_clean, specialite, username_clean, password))
            self.conn.commit()
            messagebox.showinfo("Succès", "Médecin ajouté avec succès")
            self.creer_menu_principal()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erreur", "Ce nom d'utilisateur existe déjà")
    
    def voir_medecins(self):
        # Nettoyer la fenêtre
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Titre
        titre = tk.Label(
            self.root,
            text="Liste des médecins",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c2c2c"
        )
        titre.pack(pady=20)
        
        # Frame pour la liste
        frame_liste = tk.Frame(self.root, bg="#2c2c2c")
        frame_liste.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Créer un Treeview pour afficher les médecins
        columns = ("ID", "Nom", "Spécialité", "Username")
        tree = ttk.Treeview(frame_liste, columns=columns, show="headings", height=10)
        
        # Configurer les colonnes
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        
        # Récupérer les médecins
        self.cursor.execute("SELECT id, nom_complet, specialite, nom_utilisateur FROM medecins")
        medecins = self.cursor.fetchall()
        
        # Insérer les données
        for medecin in medecins:
            tree.insert("", tk.END, values=medecin)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Bouton Retour
        btn_retour = tk.Button(
            self.root,
            text="Retour",
            command=self.creer_menu_principal,
            font=("Arial", 12),
            width=15,
            bg="white",
            fg="black"
        )
        btn_retour.pack(pady=20)
    
    def supprimer_medecin(self):
        # Récupérer la liste des médecins pour sélection
        self.cursor.execute("SELECT id, nom_complet, nom_utilisateur FROM medecins")
        medecins = self.cursor.fetchall()
        
        if not medecins:
            messagebox.showwarning("Attention", "Aucun médecin à supprimer")
            return
        
        # Créer une fenêtre de sélection
        fenetre_selection = tk.Toplevel(self.root)
        fenetre_selection.title("Supprimer un médecin")
        fenetre_selection.geometry("400x300")
        fenetre_selection.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_selection, text="Sélectionner le médecin à supprimer:",
                font=("Arial", 12, "bold"), fg="white", bg="#2c2c2c").pack(pady=20)
        
        # Listbox pour la sélection
        listbox = tk.Listbox(fenetre_selection, font=("Arial", 10), width=50, height=10)
        for medecin in medecins:
            listbox.insert(tk.END, f"Dr. {medecin[1]} ({medecin[2]})")
        listbox.pack(pady=10)
        
        def confirmer_suppression():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Attention", "Veuillez sélectionner un médecin")
                return
            
            medecin_selectionne = medecins[selection[0]]
            if messagebox.askyesno("Confirmation", 
                                  f"Supprimer définitivement Dr. {medecin_selectionne[1]} ?"):
                self.cursor.execute("DELETE FROM medecins WHERE id = ?", (medecin_selectionne[0],))
                self.conn.commit()
                messagebox.showinfo("Succès", "Médecin supprimé avec succès")
                fenetre_selection.destroy()
        
        btn_supprimer = tk.Button(fenetre_selection, text="Supprimer", 
                                 command=confirmer_suppression, bg="lightcoral", 
                                 font=("Arial", 10), width=15)
        btn_supprimer.pack(pady=10)
    
    def voir_tous_rendez_vous(self):
        """Afficher tous les rendez-vous du système avec possibilité de les gérer"""
        # Récupérer tous les rendez-vous
        self.cursor.execute('''
            SELECT rv.id, rv.date_rdv, rv.heure_rdv, p.nom_complet, m.nom_complet, 
                   m.specialite, rv.urgent, rv.statut, p.telephone
            FROM rendez_vous rv
            JOIN patients p ON rv.patient_id = p.id
            JOIN medecins m ON rv.medecin_id = m.id
            ORDER BY rv.date_rdv, rv.heure_rdv
        ''')
        
        rendez_vous = self.cursor.fetchall()
        
        # Créer fenêtre d'affichage
        fenetre_rdv = tk.Toplevel(self.root)
        fenetre_rdv.title("Tous les rendez-vous - Vue Administrateur")
        fenetre_rdv.geometry("900x600")
        fenetre_rdv.configure(bg="#2c2c2c")
        
        tk.Label(fenetre_rdv, text="Tous les rendez-vous du système", 
                font=("Arial", 14, "bold"), fg="white", bg="#2c2c2c").pack(pady=10)
        
        if not rendez_vous:
            tk.Label(fenetre_rdv, text="Aucun rendez-vous dans le système", 
                    fg="white", bg="#2c2c2c").pack(pady=50)
        else:
            # Frame pour les statistiques
            frame_stats = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_stats.pack(pady=10)
            
            # Calculer les statistiques
            total = len(rendez_vous)
            confirmes = len([r for r in rendez_vous if r[7] == 'confirmé'])
            annules = len([r for r in rendez_vous if r[7] == 'annulé'])
            urgents = len([r for r in rendez_vous if r[6] == 1])
            
            stats_text = f"Total: {total} | Confirmés: {confirmes} | Annulés: {annules} | Urgents: {urgents}"
            tk.Label(frame_stats, text=stats_text, font=("Arial", 10), 
                    fg="lightgray", bg="#2c2c2c").pack()
            
            # Frame avec scrollbar pour la liste
            frame_tree = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            # Treeview pour afficher les rendez-vous
            columns = ("Date", "Heure", "Patient", "Téléphone", "Médecin", "Spécialité", "Urgent", "Statut")
            tree = ttk.Treeview(frame_tree, columns=columns, show="headings", height=15)
            
            # Configurer les colonnes
            tree.heading("Date", text="Date")
            tree.column("Date", width=80, anchor="center")
            tree.heading("Heure", text="Heure")
            tree.column("Heure", width=60, anchor="center")
            tree.heading("Patient", text="Patient")
            tree.column("Patient", width=120, anchor="center")
            tree.heading("Téléphone", text="Téléphone")
            tree.column("Téléphone", width=100, anchor="center")
            tree.heading("Médecin", text="Médecin")
            tree.column("Médecin", width=120, anchor="center")
            tree.heading("Spécialité", text="Spécialité")
            tree.column("Spécialité", width=120, anchor="center")
            tree.heading("Urgent", text="Urgent")
            tree.column("Urgent", width=60, anchor="center")
            tree.heading("Statut", text="Statut")
            tree.column("Statut", width=80, anchor="center")
            
            # Colorer les lignes selon le statut
            tree.tag_configure("urgent", background="lightcoral")
            tree.tag_configure("annule", background="lightgray", foreground="gray")
            tree.tag_configure("normal", background="lightgreen")
            
            for rdv in rendez_vous:
                urgent_text = "OUI" if rdv[6] else "NON"
                telephone = rdv[8] if rdv[8] else "N/A"
                
                if rdv[7] == 'annulé':
                    tag = "annule"
                elif rdv[6] == 1:
                    tag = "urgent"
                else:
                    tag = "normal"
                
                tree.insert("", tk.END, values=(rdv[1], rdv[2], rdv[3], telephone, 
                           f"Dr. {rdv[4]}", rdv[5], urgent_text, rdv[7]), 
                           tags=(tag, rdv[0]))
            
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Frame pour les actions admin
            frame_actions = tk.Frame(fenetre_rdv, bg="#2c2c2c")
            frame_actions.pack(pady=10)
            
            def annuler_rdv_admin():
                """Fonction admin pour annuler un rendez-vous"""
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous")
                    return
                
                # Récupérer l'ID du rendez-vous depuis les tags
                tags = tree.item(selection[0])['tags']
                rdv_id = tags[1] if len(tags) > 1 else None  # L'ID est le 2ème tag
                rdv_values = tree.item(selection[0])['values']
                
                if rdv_values[7] == 'annulé':
                    messagebox.showwarning("Attention", "Ce rendez-vous est déjà annulé")
                    return
                
                if messagebox.askyesno("Confirmation Administrateur", 
                                     f"Annuler le rendez-vous de {rdv_values[2]} du {rdv_values[0]} à {rdv_values[1]} ?"):
                    try:
                        self.cursor.execute("UPDATE rendez_vous SET statut = 'annulé' WHERE id = ?", (rdv_id,))
                        self.conn.commit()
                        messagebox.showinfo("Succès", "Rendez-vous annulé par l'administrateur")
                        fenetre_rdv.destroy()
                        # Relancer la fenêtre pour voir la mise à jour
                        self.voir_tous_rendez_vous()
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de l'annulation: {str(e)}")
            
            def reactiver_rdv_admin():
                """Fonction admin pour réactiver un rendez-vous annulé"""
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("Attention", "Veuillez sélectionner un rendez-vous")
                    return
                
                tags = tree.item(selection[0])['tags']
                rdv_id = tags[1] if len(tags) > 1 else None
                rdv_values = tree.item(selection[0])['values']
                
                if rdv_values[7] != 'annulé':
                    messagebox.showwarning("Attention", "Ce rendez-vous n'est pas annulé")
                    return
                
                if messagebox.askyesno("Confirmation Administrateur", 
                                     f"Réactiver le rendez-vous de {rdv_values[2]} du {rdv_values[0]} à {rdv_values[1]} ?"):
                    try:
                        self.cursor.execute("UPDATE rendez_vous SET statut = 'confirmé' WHERE id = ?", (rdv_id,))
                        self.conn.commit()
                        messagebox.showinfo("Succès", "Rendez-vous réactivé par l'administrateur")
                        fenetre_rdv.destroy()
                        self.voir_tous_rendez_vous()
                    except Exception as e:
                        messagebox.showerror("Erreur", f"Erreur lors de la réactivation: {str(e)}")
            
            # Boutons d'action administrateur
            btn_annuler_admin = tk.Button(frame_actions, text="Annuler RDV", 
                                        command=annuler_rdv_admin, bg="lightcoral", font=("Arial", 10))
            btn_annuler_admin.pack(side=tk.LEFT, padx=10)
            
            btn_reactiver_admin = tk.Button(frame_actions, text="Réactiver RDV", 
                                          command=reactiver_rdv_admin, bg="lightblue", font=("Arial", 10))
            btn_reactiver_admin.pack(side=tk.LEFT, padx=10)
            
            # Bouton retour
            btn_retour = tk.Button(frame_actions, text="Retour", 
                                 command=fenetre_rdv.destroy, bg="lightgray", font=("Arial", 10))
            btn_retour.pack(side=tk.RIGHT, padx=10)
            
            # Note explicative
            tk.Label(fenetre_rdv, text="Rouge: Urgent | Gris: Annulé | Vert: Normal | Sélectionnez un RDV puis utilisez les boutons", 
                    font=("Arial", 9), fg="lightgray", bg="#2c2c2c").pack(pady=5)
    
    def deconnexion(self):
        self.admin_connecte = False
        self.creer_interface_connexion()
    
    def quitter(self):
        self.conn.close()
        self.root.quit()
        self.root.destroy()
        

root = tk.Tk()
app = EspaceAdministrateur(root)
root.mainloop()