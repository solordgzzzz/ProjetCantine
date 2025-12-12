import tkinter as tk

# Palette élégante (un peu ajustée)
BG_COLOR = "#0f172a"          # Fond gris-bleu très sombre
CARD_COLOR = "#111827"        # Encadré question / conteneur
BUTTON_COLOR = "#3b82f6"      # Boutons bleu doux
BUTTON_HOVER = "#2563eb"
TEXT_COLOR = "#e5e7eb"        # Texte principal
MSG_COLOR = "#22c55e"         # Message succès (vert)
CARD_BORDER = "#4b5563"
ERROR_COLOR = "#f97373"       # Pour messages d’erreur éventuels


class IHM:
    """Interface de vote RFID avec design pro et texte centré."""

    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Système de Vote RFID")
        self.root.configure(bg=BG_COLOR)

        # Plein écran adaptatif
        try:
            self.root.state("zoomed")
        except Exception:
            self.root.attributes("-fullscreen", True)

        self.root.resizable(True, True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        # Typo
        self.font_title = ("Helvetica", 30, "bold")
        self.font_vote = ("Helvetica", 18)
        self.font_button = ("Helvetica", 22, "bold")
        self.font_stats = ("Helvetica", 18, "bold")
        self.font_msg = ("Helvetica", 20, "italic")

        # Conteneur global centré
        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(expand=True, fill="both", padx=40, pady=40)

        # Encadré question
        self.question_frame = tk.Frame(
            self.main_frame,
            bg=CARD_COLOR,
            bd=2,
            relief="ridge",
            highlightthickness=2,
            highlightbackground=CARD_BORDER,
        )
        self.question_frame.pack(pady=20, fill="x")

        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=self.font_title,
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
            wraplength=1000,
            justify="center",
            pady=30,
        )
        self.question_label.pack(padx=30, pady=10)

        # Sous-texte / instructions (optionnel)
        self.subtitle_label = tk.Label(
            self.main_frame,
            text="Choisissez une réponse puis scannez votre badge.",
            font=self.font_vote,
            fg="#9ca3af",
            bg=BG_COLOR,
        )
        self.subtitle_label.pack(pady=(10, 0))

        # Frame pour les boutons de choix
        self.choix_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.choix_frame.pack(pady=40)

        # Label pour les messages centré
        self.msg_label = tk.Label(
            self.main_frame,
            text="",
            font=self.font_msg,
            fg=MSG_COLOR,
            bg=BG_COLOR,
            wraplength=800,
            justify="center",
        )
        self.msg_label.pack(pady=(10, 0))

    def demander_choix(self, question, listeChoix):
        self.question_label.config(text=question)
        self.msg_label.config(text="")  # Nettoyer ancien message

        # Nettoie les anciens boutons
        for widget in self.choix_frame.winfo_children():
            widget.destroy()

        # Réordonner les choix si on a exactement ceux-là
        mapping_ordre = ["Éclaté", "Bof", "bon", "Excellent"]
        ordre_personnalise = [c for c in mapping_ordre if c in listeChoix]

        if len(ordre_personnalise) == len(listeChoix):
            liste_affichee = ordre_personnalise
        else:
            liste_affichee = listeChoix

        # Configuration colonnes pour bonne répartition
        self.choix_frame.columnconfigure(0, weight=1, pad=20)
        self.choix_frame.columnconfigure(1, weight=1, pad=20)

        # Afficher sur 2 colonnes
        for idx, choix in enumerate(liste_affichee):
            row = idx // 2
            col = idx % 2
            index_vote = idx + 1

            b = tk.Button(
                self.choix_frame,
                text=choix,
                width=14,
                font=self.font_button,
                bg=BUTTON_COLOR,
                fg="white",
                activebackground=BUTTON_HOVER,
                activeforeground="white",
                bd=0,
                relief="flat",
                cursor="hand2",
                command=lambda i=index_vote: self.on_choix(i),
            )
            b.grid(row=row, column=col, padx=30, pady=18, sticky="ew")

            # Effet hover
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=BUTTON_HOVER))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=BUTTON_COLOR))

    def on_choix(self, choix):
        """Transmet le choix (index 1..4) au contrôleur et affiche un feedback."""
        self.controller.choix_fait(choix)
        self.afficher_message(f"Vous avez choisi : {choix}\nVeuillez scanner votre badge RFID")

    def afficher_message(self, message, error=False):
        """Affiche un message centré à l'écran."""
        self.msg_label.config(
            text=message,
            fg=ERROR_COLOR if error else MSG_COLOR,
        )

    def demarrer(self):
        self.root.mainloop()
