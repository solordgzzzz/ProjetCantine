import tkinter as tk
from tkinter import messagebox, simpledialog
import random, json
from paho.mqtt import client as mqtt_client
from vote import Vote

# --- Config MQTT ---
BROKER = '192.168.190.17'
PORT = 1883
TOPIC_QUESTION = 'cantine/question'
USERNAME = "crdg"
PASSWORD = "crdg*123"

# Palette élégante
BG_COLOR = "#1f2937"          # Fond principal (gris foncé)
CARD_COLOR = "#374151"        # Cartes de vote (gris légèrement clair)
CARD_HIGHLIGHT = "#2563eb"    # Dernier vote (bleu doux)
TEXT_COLOR = "#f9fafb"        # Texte clair
BUTTON_COLOR = "#3b82f6"      # Bouton bleu doux
BUTTON_HOVER = "#2563eb"

class InterfaceChef:
    """Client MQTT pour recevoir et envoyer les votes."""

    def __init__(self, controller):
        self.controller = controller
        self.topic_vote = 'cantine/pupitre/+/vote'
        self.client_id = f'Chef-{random.randint(0, 1000)}'
        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT pour les votes")
            self.client.subscribe(self.topic_vote)
        else:
            print(f"Erreur connexion MQTT, code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload_str = msg.payload.decode('utf-8').strip()
            if not payload_str:
                return
            try:
                payload = json.loads(payload_str)
                vote = Vote.fromJson(payload)
                vote_str = f"ID: {vote.id} → {vote.choix}"
            except Exception:
                vote_str = f"Vote reçu: {payload_str}"
            self.controller.ajouter_vote(vote_str)
        except Exception as e:
            print(f"Erreur traitement vote: {e}")

    def envoyerVote(self, vote):
        msg = vote.toJson()
        self.client.publish(f'cantine/pupitre/{vote.id}/vote', msg)
        vote_str = f"TON VOTE: ID={vote.id} → {vote.choix}"
        self.controller.ajouter_vote(vote_str)

    def envoyerQuestion(self, question, choix):
        message = {"question": question, "choix": choix}
        self.client.publish(TOPIC_QUESTION, json.dumps(message, ensure_ascii=False))


class IHM:
    """Dashboard moderne et élégant Tkinter avec scroll pour votes."""

    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("📊 Dashboard Votes Cantine")
        self.root.configure(bg=BG_COLOR)

        # --- 💡 FULLSCREEN ADAPTATIF ---
        try:
            self.root.state('zoomed')  # Windows
        except:
            self.root.attributes('-fullscreen', True)  # Linux / Mac

        self.root.resizable(True, True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.font_title = ("Helvetica", 18, "bold")
        self.font_vote = ("Helvetica", 14)
        self.font_button = ("Helvetica", 13, "bold")

        # Label question
        self.label_question = tk.Label(self.root, text="", font=self.font_title,
                                       fg=TEXT_COLOR, bg=BG_COLOR)
        self.label_question.pack(pady=15)

        # --- Frame principale responsive
        self.frame_container = tk.Frame(self.root, bg=BG_COLOR)
        self.frame_container.pack(pady=10, fill=tk.BOTH, expand=True)

        # Canvas pour les votes
        self.canvas = tk.Canvas(self.frame_container, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar verticale
        self.scrollbar = tk.Scrollbar(self.frame_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame interne pour votes
        self.frame_votes = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window((0, 0), window=self.frame_votes, anchor="nw")

        self.frame_votes.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Bouton modifier question (centré)
        self.btn_modifier = tk.Button(
            self.root,
            text="Modifier la question",
            font=self.font_button,
            bg=BUTTON_COLOR,
            fg="white",
            activebackground=BUTTON_HOVER,
            activeforeground="white",
            padx=20,
            pady=10,
            bd=0,
            relief="flat",
            command=self.demander_modification
        )
        self.btn_modifier.pack(pady=15)

        # Compteur de votes
        self.vote_count = 0
        self.label_count = tk.Label(self.root, text=f"Votes reçus : {self.vote_count}",
                                    font=self.font_vote, fg=TEXT_COLOR, bg=BG_COLOR)
        self.label_count.pack(pady=5)

    def demander_choix(self, question, listeChoix=None):
        self.label_question.config(text=question)

    def afficher_message(self, message):
        messagebox.showinfo("Information", message)

    def ajouter_vote(self, vote_str):
        self.root.after(0, self._add_vote_card, vote_str)

    def _add_vote_card(self, vote_str):
        card = tk.Label(self.frame_votes, text=vote_str, font=self.font_vote,
                        bg=CARD_COLOR, fg=TEXT_COLOR, padx=10, pady=5, bd=0, relief="flat")
        card.pack(pady=3, fill=tk.X, padx=20)

        card.after(100, lambda: card.config(bg=CARD_HIGHLIGHT))
        card.after(700, lambda: card.config(bg=CARD_COLOR))

        self.vote_count += 1
        self.label_count.config(text=f"Votes reçus : {self.vote_count}")
        self.canvas.yview_moveto(1.0)  # Scroll auto vers bas

    def demander_modification(self):
        question = simpledialog.askstring("Nouvelle question", "Entrez la nouvelle question :")
        if not question:
            return
        choix_str = simpledialog.askstring("Choix", "Entrez les choix séparés par des virgules :")
        if not choix_str:
            return
        listeChoix = [c.strip() for c in choix_str.split(",")]
        self.controller.modifierQuestion(question, listeChoix)

    def start(self):
        self.root.mainloop()


class ControllerChef:
    def __init__(self):
        self.question = "Comment avez-vous trouvé le repas ?"
        self.listeChoix = ["Éclaté", "bof", "Bon", "Excellent"]
        self.ihm = IHM(self)
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.interface_mqtt = InterfaceChef(self)
        self.publier_question()

    def modifierQuestion(self, question, listeChoix):
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Nouvelle question reçue !")
        self.publier_question()

    def publier_question(self):
        self.interface_mqtt.envoyerQuestion(self.question, self.listeChoix)
        print(f"Question publiée : {self.question} / {self.listeChoix}")

    def ajouter_vote(self, vote_str):
        self.ihm.ajouter_vote(vote_str)

    def envoyer_vote(self, vote):
        self.interface_mqtt.envoyerVote(vote)

    def start(self):
        self.ihm.start()


if __name__ == "__main__":
    app = ControllerChef()
    app.start()
