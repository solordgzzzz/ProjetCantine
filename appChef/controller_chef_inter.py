import tkinter as tk
from tkinter import messagebox, simpledialog
import random, json
from paho.mqtt import client as mqtt_client
from statistiques import Statistique
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Config MQTT ---
BROKER = '192.168.190.15'
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
BUTTON_HOVER = "#2563eb"


class InterfaceChef:
    """Client MQTT pour recevoir et envoyer les votes/questions."""

    def __init__(self, controller):
        self.controller = controller
        self.topic_vote = 'cantine/pupitre/+/vote'
        self.topic_stats = 'cantine/stats_votes'
        self.stats = None
        self.last_question = None  # ← stocke la dernière question reçue
        self.client_id = f'Chef-{random.randint(0, 1000)}'
        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT")
            self.client.subscribe(self.topic_vote)
            self.client.subscribe(self.topic_stats)
            self.client.subscribe(TOPIC_QUESTION)  # récupérer la dernière question
        else:
            print(f"Erreur connexion MQTT, code {rc}")

    def on_message(self, client, userdata, msg):
        payload_str = msg.payload.decode('utf-8').strip()
        print(f"[MQTT] {msg.topic} → {payload_str}")

        try:
            data = json.loads(payload_str)
        except:
            return

        # --- stats ---
        if msg.topic == self.topic_stats:
            self.stats = data
            return

        # --- question ---
        if msg.topic == TOPIC_QUESTION:
            question = data.get("question")
            choix = data.get("choix")
            if question and choix:
                self.last_question = (question, choix)  # ← stocker la question
                if hasattr(self.controller, "ihm") and self.controller.ihm.root.winfo_exists():
                    # Thread-safe update
                    self.controller.ihm.root.after(0, self.controller.ihm.demander_choix, question, choix)
                    # Mettre à jour le controller également
                    self.controller.question = question
                    self.controller.listeChoix = choix

    def envoyerQuestion(self, question, choix):
        message = {"question": question, "choix": choix}
        self.client.publish(
            TOPIC_QUESTION,
            json.dumps(message, ensure_ascii=False),
            retain=True  # <-- important
        )


class IHM:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("📊 Dashboard Votes Cantine")
        self.root.configure(bg=BG_COLOR)

        try:
            self.root.state('zoomed')
        except Exception:
            self.root.attributes('-fullscreen', True)

        self.root.resizable(True, True)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.font_title = ("Helvetica", 22, "bold")
        self.font_vote = ("Helvetica", 14)
        self.font_button = ("Helvetica", 13, "bold")
        self.font_stats = ("Helvetica", 20, "bold")

        # Label question
        self.label_question = tk.Label(self.root, text="", font=self.font_title,
                                       fg=TEXT_COLOR, bg=BG_COLOR)
        self.label_question.pack(pady=15)

        # Stats + camembert
        self.stats_pie_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.stats_pie_frame.pack(pady=10, expand=True)

        self.frame_pie = tk.Frame(self.stats_pie_frame, bg=BG_COLOR)
        self.frame_pie.pack(side="left", padx=20, pady=5)

        self.fig = Figure(figsize=(3.5, 3.5), dpi=100)
        self.ax_pie = self.fig.add_subplot(111)
        self.canvas_pie = FigureCanvasTkAgg(self.fig, master=self.frame_pie)
        self.canvas_pie.get_tk_widget().pack()

        self.label_stats = tk.Label(self.stats_pie_frame, text="", font=self.font_stats,
                                    fg=TEXT_COLOR, bg=BG_COLOR, justify="left")
        self.label_stats.pack(side="left", padx=40, pady=5)

        # Liste des votes
        self.frame_container = tk.Frame(self.root, bg=BG_COLOR)
        self.frame_container.pack(pady=10, fill=tk.BOTH)

        self.canvas = tk.Canvas(self.frame_container, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.frame_container, orient=tk.VERTICAL,
                                      command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.frame_votes = tk.Frame(self.canvas, bg=BG_COLOR)
        self.canvas.create_window((0, 0), window=self.frame_votes, anchor="nw")

        self.frame_votes.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        # Bas
        self.bottom_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.bottom_frame.pack(pady=10)

        self.btn_modifier = tk.Button(self.bottom_frame, text="Modifier la question",
                                      font=self.font_button, bg=BUTTON_COLOR, fg="white",
                                      activebackground=BUTTON_HOVER, activeforeground="white",
                                      padx=20, pady=10, bd=0, relief="flat",
                                      command=self.demander_modification)
        self.btn_modifier.pack(side="left", padx=10)

        self.vote_count = 0
        self.label_count = tk.Label(self.bottom_frame, text="0", font=self.font_button,
                                    fg=TEXT_COLOR, bg=BG_COLOR)
        self.label_count.pack(side="left", padx=10)

        self.mettre_a_jour_stats()

    def demander_choix(self, question, listeChoix=None):
        self.label_question.config(text=question)

    def afficher_message(self, message):
        messagebox.showinfo("Information", message)

    def ajouter_vote(self, vote_str):
        self.root.after(0, self._add_vote_card, vote_str)

    def _add_vote_card(self, vote_str):
        card = tk.Label(self.frame_votes, text=vote_str, font=self.font_vote,
                        bg=CARD_COLOR, fg=TEXT_COLOR, padx=10, pady=5,
                        bd=0, relief="flat")
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
            self.label_stats.config(text="Aucune statistique disponible.")
            return

        votes_par_choix = stats["stats"]
        if not votes_par_choix:
            self.label_stats.config(text="Données insuffisantes.")
            return

        total_votes = sum(votes_par_choix)
        if total_votes == 0:
            self.label_stats.config(text="Aucun vote enregistré.")
            self.ax_pie.clear()
            self.canvas_pie.draw()
            return

        pourcentages = Statistique.calculer_pourcentages(stats)
        if pourcentages is None:
            self.label_stats.config(text="Erreur calcul.")
            return

        noms = getattr(self.controller, "listeChoix", None)
        lignes = ["📊 Statistiques des votes:"]
        for i, nb_votes in enumerate(votes_par_choix):
            nom = noms[i] if noms and i < len(noms) else f"Choix {i+1}"
            lignes.append(f"{nom}: {nb_votes} votes ({pourcentages[i]:.1f}%)")
        lignes.append(f"Total: {total_votes} votes")
        self.label_stats.config(text="\n".join(lignes))

        self.ax_pie.clear()
        labels = noms if noms and len(noms) == len(votes_par_choix) else [f"Choix {i+1}" for i in range(len(votes_par_choix))]
        self.ax_pie.pie(votes_par_choix, labels=labels, startangle=90)
        self.ax_pie.axis("equal")
        self.canvas_pie.draw()

    def mettre_a_jour_stats(self):
        self.voir_stat()
        self.root.after(1000, self.mettre_a_jour_stats)

    def start(self):
        self.root.mainloop()


class ControllerChef:
    def __init__(self):
        self.question = None
        self.listeChoix = None

        # ⚠️ Créer MQTT avant IHM
        self.interface_mqtt = InterfaceChef(self)
        self.ihm = IHM(self)

        # Si une question a déjà été reçue, l’afficher
        if self.interface_mqtt.last_question:
            question, choix = self.interface_mqtt.last_question
            self.ihm.demander_choix(question, choix)
            self.question = question
            self.listeChoix = choix

        print("En attente de la question depuis MQTT…")

    def modifierQuestion(self, question, listeChoix):
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(question, listeChoix)
        self.interface_mqtt.envoyerQuestion(question, listeChoix)
        self.ihm.afficher_message("Nouvelle question envoyée !")

    def obtenir_statistiques(self):
        return self.interface_mqtt.stats

    def start(self):
        self.ihm.start()


if __name__ == "__main__":
    app = ControllerChef()
    app.start()
