import tkinter as tk
from tkinter import messagebox, simpledialog


class IHM:
    def __init__(self, controller):
        self.controller = controller

        # Fenêtre principale
        self.root = tk.Tk()
        self.root.title("Système de votes - Chef")

        # Label pour la question
        self.label_question = tk.Label(self.root, text="", font=("Arial", 14))
        self.label_question.pack(pady=10)

        # Frame pour les boutons (choix)
        self.frame_choix = tk.Frame(self.root)
        self.frame_choix.pack(pady=10)

        # Bouton pour modifier la question
        self.btn_modifier = tk.Button(
            self.root, text="Modifier la question", command=self.demander_modification
        )
        self.btn_modifier.pack(pady=10)

    def demander_choix(self, question, listeChoix):
        """Affiche la question et les choix dans l'interface"""
        self.label_question.config(text=question)

        # Nettoyer les anciens boutons
        for widget in self.frame_choix.winfo_children():
            widget.destroy()

        # Créer les nouveaux boutons de vote
        for choix in listeChoix:
            tk.Button(
                self.frame_choix,
                text=choix,
                font=("Arial", 12),
                width=15,
                command=lambda c=choix: self.controller.recevoir_vote(c)
            ).pack(pady=3)

    def afficher_message(self, message):
        messagebox.showinfo("Information", message)

    def demander_modification(self):
        """Demande à l'utilisateur une nouvelle question + les choix"""
        question = simpledialog.askstring("Nouvelle question", "Entrez la nouvelle question :")
        if not question:
            return
        
        choix = simpledialog.askstring(
            "Choix", "Entrez les choix séparés par des virgules (ex: Oui,Non,Peut-être) :"
        )
        if not choix:
            return

        listeChoix = [c.strip() for c in choix.split(",")]
        self.controller.modifierQuestion(question, listeChoix)

    def start(self):
        self.root.mainloop()


class Controller_chef:
    def __init__(self):
        self.question = "Comment avez-vous trouvé le repas ?"
        self.listeChoix = ['Éclaté', 'Bof', 'Bon', 'Excellent']

        self.ihm = IHM(self)
        self.ihm.demander_choix(self.question, self.listeChoix)

    def modifierQuestion(self, question, listeChoix):
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Nouvelle question reçue !")

    def recevoir_vote(self, choix):
        messagebox.showinfo("Vote enregistré", f"Vous avez voté : {choix}")

    def start(self):
        self.ihm.start()


# Lancer l'application
if __name__ == "__main__":
    app = Controller_chef()
    app.start()
