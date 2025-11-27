import tkinter as tk
from tkinter import messagebox, simpledialog
import random, json
from paho.mqtt import client as mqtt_client
from statistiques import Statistique


# --- Config MQTT ---
BROKER = '192.168.190.17'
PORT = 1883
TOPIC_QUESTION = 'cantine/question'
USERNAME = "crdg"
PASSWORD = "crdg*123"


# Palette élégante
BG_COLOR = "#1f2937"
CARD_COLOR = "#374151"
CARD_HIGHLIGHT = "#2563eb"
TEXT_COLOR = "#f9fafb"
BUTTON_COLOR = "#3b82f6"
BUTTON_COLOR_STAT = "#C72626"  
BUTTON_HOVER = "#2563eb"


class InterfaceChef:
    """Client MQTT pour recevoir et envoyer les votes."""

    def __init__(self, controller):
        self.controller = controller
        self.topic_stats = 'cantine/stats_votes'
        self.stats = None  # Mis à jour automatiquement
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
            self.client.subscribe(self.topic_stats)  # Écoute en continu
        else:
            print(f"Erreur connexion MQTT, code {rc}")

    def on_message(self, client, userdata, msg):
        payload_str = msg.payload.decode('utf-8').strip()
        print(f"Message reçu sur {msg.topic} : {payload_str}")

        self.stats = json.loads(payload_str)

    def envoyerQuestion(self, question, choix):
        message = {"question": question, "choix": choix}
        self.client.publish(TOPIC_QUESTION, json.dumps(message, ensure_ascii=False))

class IHM:
    
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("📊 Dashboard Votes Cantine")
        self.root.configure(bg=BG_COLOR)

        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-fullscreen', True)

        self.root.resizable(True, True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.font_title = ("Helvetica", 18, "bold")
        self.font_vote = ("Helvetica", 14)
        self.font_button = ("Helvetica", 13, "bold")

        # Label question
        self.label_question = tk.Label(self.root, text="", font=self.font_title,
                                       fg=TEXT_COLOR, bg=BG_COLOR)
        self.label_question.pack(pady=15)

        # Frame principale
        self.frame_container = tk.Frame(self.root, bg=BG_COLOR)
        self.frame_container.pack(pady=10, fill=tk.BOTH, expand=True)

        # Canvas pour les votes
        self.canvas = tk.Canvas(self.frame_container, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.frame_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame interne pour votes
        self.frame_votes = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window((0, 0), window=self.frame_votes, anchor="nw")

        self.frame_votes.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.bottom_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.bottom_frame.pack(pady=15)

        # Bouton : Modifier la question
        self.btn_modifier = tk.Button(
            self.bottom_frame,
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
        self.btn_modifier.pack(side="left", padx=10)

        # Bouton : voir statistique
        self.btn_statistique = tk.Button(
            self.bottom_frame,
            text="Voir statistique",
            font=self.font_button,
            bg=BUTTON_COLOR_STAT,
            fg="white",
            activebackground=BUTTON_HOVER,
            activeforeground="white",
            padx=20,
            pady=10,
            bd=0,
            relief="flat",
            command=self.voir_stat
        )
        self.btn_statistique.pack(side="left", padx=10)



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
        self.label_count.config(text=f"{self.vote_count}")
        self.canvas.yview_moveto(1.0)

    def demander_modification(self):
        question = simpledialog.askstring("Nouvelle question", "Entrez la nouvelle question :")
        if not question:
            return
        choix_str = simpledialog.askstring("Choix", "Entrez les choix séparés par des virgules :")
        if not choix_str:
            return
        listeChoix = [c.strip() for c in choix_str.split(",")]
        self.controller.modifierQuestion(question, listeChoix)

    def voir_stat(self):
        stats = self.controller.obtenir_statistiques()

        if not stats or "stats" not in stats:
            self.label_stats.config(text="Aucune statistique disponible pour le moment.")
            return

        votes_par_choix = stats["stats"]
        if len(votes_par_choix) < 1:
            self.label_stats.config(text="Données insuffisantes.")
            return

        total_votes = sum(votes_par_choix)
        if total_votes == 0:
            self.label_stats.config(text="Aucun vote enregistré.")
            return

        # Appel de la fonction de calcul
        pourcentages = Statistique.calculer_pourcentages(stats)
        if pourcentages is None:
            self.label_stats.config(text="Erreur lors du calcul des pourcentages.")
            return

        # Construction du texte à afficher sous la question
        lignes = ["📊 Statistiques des votes:"]
        for i, nb_votes in enumerate(votes_par_choix, start=1):
            p = pourcentages[i - 1]
            lignes.append(f"Choix {i}: {nb_votes} votes ({p:.1f}%)")

        lignes.append(f"Total: {total_votes} votes")
        self.label_stats.config(text="\n".join(lignes))





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

    def obtenir_statistiques(self):
        return self.interface_mqtt.stats

    def start(self):
        self.ihm.start()


if __name__ == "__main__":
    app = ControllerChef()
    app.start()