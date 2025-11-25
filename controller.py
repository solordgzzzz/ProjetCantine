from interfaceVotes import InterfaceVotes
from vote import Vote
from rfid2 import RFID2
from ihm_inter import IHM
import paho.mqtt.client as mqtt
import json
import threading

BROKER = '192.168.190.17'
PORT = 1883
TOPIC_QUESTION = 'cantine/question'
USERNAME = "crdg"
PASSWORD = "crdg*123"


class Controller:
    def __init__(self):
        # Question par défaut au démarrage
        self.question = "Comment avez-vous trouvé le repas ?"
        self.listeChoix = ['Éclaté', 'bof', 'Bon', 'Excellent']

        self.rfid = RFID2()
        self.ihm = IHM(self)  # Passe le controller à IHM
        self.interfaceVotes = InterfaceVotes(1, self)
        self.interfaceVotes.connecter()

        # Pour l'affichage initial
        self.ihm.demander_choix(self.question, self.listeChoix)

        # MQTT client pour récupérer la question en temps réel
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(USERNAME, PASSWORD)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(BROKER, PORT, 60)
        self.mqtt_client.loop_start()  # Boucle en arrière-plan

    # Connexion au broker MQTT
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT")
            client.subscribe(TOPIC_QUESTION)
        else:
            print(f"Erreur de connexion MQTT, code: {rc}")

    # Message reçu sur le topic
    def on_message(self, client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            self.question = data.get("question", self.question)
            self.listeChoix = data.get("choix", self.listeChoix)
            # Met à jour l'IHM si elle existe
            if hasattr(self, 'ihm'):
                self.ihm.demander_choix(self.question, self.listeChoix)
                self.ihm.afficher_message("Question mise à jour depuis MQTT !")
        except Exception as e:
            print("Erreur lors du traitement du message MQTT :", e)

    def voter(self):
        # Lance la boucle principale de Tkinter
        self.id_votant = None
        self.demander_badge()
        self.ihm.demarrer()

    def demander_badge(self):
        self.ihm.afficher_message("Veuillez scanner votre badge RFID")
        # Lance la lecture RFID dans un thread si besoin
        threading.Thread(target=self.lire_rfid, daemon=True).start()

    def lire_rfid(self):
        self.id_votant = self.rfid.lireRfid()
        self.ihm.afficher_message("Badge détecté ! Veuillez voter.")

    def choix_fait(self, choix):
        if self.id_votant is not None:
            vote = Vote(self.id_votant, choix)
            status = self.interfaceVotes.envoyerVote(vote)
            if status[0] == 0:
                self.ihm.afficher_message("Le vote a été transmis")
            else:
                self.ihm.afficher_message(str(status))
            self.id_votant = None
            self.demander_badge()  # Redemande un vote

    def modifierQuestion(self, question, listeChoix):
        """Change la question depuis l'IHM et l'envoie sur MQTT"""
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Nouvelle question envoyée !")
        self.interfaceVotes.envoyerQuestion(self.question, self.listeChoix)


if __name__ == "__main__":
    app = Controller()
    app.voter()
