import tkinter as tk
from tkinter import messagebox, simpledialog
import paho.mqtt.client as mqtt
import json

BROKER = '192.168.190.17'
PORT = 1883
TOPIC_QUESTION = 'cantine/question'
USERNAME = "crdg"
PASSWORD = "crdg*123"


class IHM:
    def __init__(self, controller):
        self.controller = controller

        self.root = tk.Tk()
        self.root.title("Système de votes - Chef")

        # Label pour afficher la question
        self.label_question = tk.Label(self.root, text="", font=("Arial", 14))
        self.label_question.pack(pady=20)

        # Bouton pour modifier la question
        self.btn_modifier = tk.Button(
            self.root,
            text="Modifier la question",
            font=("Arial", 12),
            command=self.demander_modification
        )
        self.btn_modifier.pack(pady=10)

    def demander_choix(self, question, listeChoix=None):
        self.label_question.config(text=question)

    def afficher_message(self, message):
        messagebox.showinfo("Information", message)

    def demander_modification(self):
        question = simpledialog.askstring("Nouvelle question", "Entrez la nouvelle question :")
        if not question:
            return
        
        choix_str = simpledialog.askstring(
            "Choix", "Entrez les choix séparés par des virgules (ex: Éclaté,bof,Bon,Excellent) :"
        )
        if not choix_str:
            return

        listeChoix = [c.strip() for c in choix_str.split(",")]
        self.controller.modifierQuestion(question, listeChoix)

    def start(self):
        self.root.mainloop()


class Controller_chef:
    def __init__(self, mqtt_broker=BROKER, mqtt_port=PORT, topic=TOPIC_QUESTION,
                 username=USERNAME, password=PASSWORD):
        self.question = "Comment avez-vous trouvé le repas ?"
        self.listeChoix = ["Éclaté", "bof", "Bon", "Excellent"]
        self.topic = topic

        # MQTT avec authentification
        self.client = mqtt.Client()
        self.client.username_pw_set(username, password)  # <-- Authentification
        self.client.on_connect = self.on_connect
        self.client.connect(mqtt_broker, mqtt_port, 60)
        self.client.loop_start()  # Assure que la boucle tourne en arrière-plan

        # Interface
        self.ihm = IHM(self)
        self.ihm.demander_choix(self.question, self.listeChoix)

        # Publier la question initiale
        self.publier_question()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT")
        else:
            print(f"Erreur de connexion MQTT, code: {rc}")

    def modifierQuestion(self, question, listeChoix):
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Nouvelle question reçue !")
        self.publier_question()

    def publier_question(self):
        """Publie la question et les choix sur MQTT au format JSON"""
        message = json.dumps({
            "question": self.question,
            "choix": self.listeChoix
        }, ensure_ascii=False)  # <-- garder les accents correctement
        result = self.client.publish(self.topic, message)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Question publiée sur MQTT : {message}")
        else:
            print("Erreur lors de la publication MQTT")


    def start(self):
        self.ihm.start()


# Lancer l'application
if __name__ == "__main__":
    app = Controller_chef()
    app.start()
