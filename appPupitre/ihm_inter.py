import tkinter as tk

# Palette élégante
BG_COLOR = "#1f2937"          # Fond gris foncé
CARD_COLOR = "#374151"        # Encadré question / conteneur
BUTTON_COLOR = "#3b82f6"      # Boutons bleu doux
BUTTON_HOVER = "#2563eb"
TEXT_COLOR = "#f9fafb"        # Texte principal
MSG_COLOR = "#10b981"         # Message succès (vert doux)
CARD_BORDER = "#4b5563"


class IHM:
    """Interface de vote RFID avec design pro et texte centré."""

    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("📋 Système de Vote RFID")
        self.root.configure(bg=BG_COLOR)

        # Ouvrir en plein écran et s'adapte à toutes les résolutions
        try:
            self.root.state('zoomed')  # Windows
        except Exception:
            self.root.attributes('-fullscreen', True)  # Mac / Linux

        self.root.resizable(True, True)

        # Sortir du plein écran avec ECHAP
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.font_title = ("Helvetica", 18, "bold")
        self.font_button = ("Helvetica", 14, "bold")
        self.font_msg = ("Helvetica", 16, "italic")  # un peu plus grand pour centrage

        # Encadré question
        self.question_frame = tk.Frame(self.root, bg=CARD_COLOR, bd=2, relief="ridge")
        self.question_frame.pack(pady=20, padx=20, fill="x")

        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=self.font_title,
            fg=TEXT_COLOR,
            bg=CARD_COLOR,
            wraplength=800,
            justify="center",
            pady=20,
        )
        self.question_label.pack()

        # Frame pour les boutons de choix
        self.choix_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.choix_frame.pack(pady=10)

        # Label pour les messages centré
        self.msg_label = tk.Label(
            self.root,
            text="",
            font=self.font_msg,
            fg=MSG_COLOR,
            bg=BG_COLOR,
            wraplength=800,
            justify="center",
        )
        # Centrer le label au milieu de l'écran
        self.msg_label.place(relx=0.5, rely=0.6, anchor="center")

    def demander_choix(self, question, listeChoix):
        self.question_label.config(text=question)
        for widget in self.choix_frame.winfo_children():
            widget.destroy()

        for idx, choix in enumerate(listeChoix):
            b = tk.Button(
                self.choix_frame,
                text=choix,
                width=30,
                font=self.font_button,
                bg=BUTTON_COLOR,
                fg="white",
                activebackground=BUTTON_HOVER,
                activeforeground="white",
                bd=0,
                relief="flat",
                command=lambda i=idx + 1: self.on_choix(i),
            )
            b.pack(pady=8)

            # Effet hover
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=BUTTON_HOVER))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=BUTTON_COLOR))

    def on_choix(self, choix):
        """Transmet le choix au contrôleur et affiche un feedback."""
        self.controller.choix_fait(choix)
        self.afficher_message(f"Vous avez choisi : {choix}")
        self.afficher_message("Veuillez scanner votre badge RFID")

    def afficher_message(self, message):
        """Affiche un message centré à l'écran."""
        self.msg_label.config(text=message)

    def demarrer(self):
        self.root.mainloop()
