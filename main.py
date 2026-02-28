import tkinter as tk
import subprocess
import sys

class SystemeGestionRendezVous:
    def __init__(self, root):
        self.root = root
        self.root.title("Système de gestion des rendez-vous médicaux")
        self.root.geometry("500x400")
        self.root.configure(bg="#2c2c2c")
        
        # Centrer la fenêtre
        self.centrer_fenetre()
        
        # Créer l'interface
        self.creer_interface()
    
    def centrer_fenetre(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def creer_interface(self):
        # Titre principal
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
        
        # Bouton Espace Patient
        btn_patient = tk.Button(
            frame_boutons,
            text="Espace Patient",
            command=self.ouvrir_espace_patient,
            **style_bouton
        )
        btn_patient.pack(pady=10)
        
        # Bouton Espace Médecin
        btn_medecin = tk.Button(
            frame_boutons,
            text="Espace Médecin",
            command=self.ouvrir_espace_medecin,
            **style_bouton
        )
        btn_medecin.pack(pady=10)
        
        # Bouton Espace Administrateur
        btn_admin = tk.Button(
            frame_boutons,
            text="Espace Administrateur",
            command=self.ouvrir_espace_admin,
            **style_bouton
        )
        btn_admin.pack(pady=10)
        
        # Bouton Quitter
        btn_quitter = tk.Button(
            frame_boutons,
            text="Quitter",
            command=self.quitter_application,
            **style_bouton
        )
        btn_quitter.pack(pady=10)
    
    def ouvrir_espace_patient(self):
        try:
            subprocess.Popen([sys.executable, "patient.py"])
        except FileNotFoundError:
            print("Fichier patient.py non trouvé")
    
    def ouvrir_espace_medecin(self):
        try:
            subprocess.Popen([sys.executable, "medecin.py"])
        except FileNotFoundError:
            print("Fichier medecin.py non trouvé")
    
    def ouvrir_espace_admin(self):
        try:
            subprocess.Popen([sys.executable, "admin.py"])
        except FileNotFoundError:
            print("Fichier admin.py non trouvé")
    
    def quitter_application(self):
        self.root.quit()
        self.root.destroy()


root = tk.Tk()
app = SystemeGestionRendezVous(root)
root.mainloop()