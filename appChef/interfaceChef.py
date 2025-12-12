import random, json
from paho.mqtt import client as mqtt_client


class InterfaceChef:

    BROKER = '192.168.190.15'
    PORT = 1883
    TOPIC_QUESTION = 'cantine/question'
    TOPIC_VOTES = 'cantine/statsvotes'
    USERNAME = "crdg"
    PASSWORD = "crdg*123"

    def __init__(self, num_pupitre, controller):
        # topic de vote pour ce pupitre
        self.topic = f'cantine/pupitre/+/vote'

        # client MQTT
        self.client_id = f'Cantine-{random.randint(0, 1000)}'
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,
                                         client_id=self.client_id)
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)

        # callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.controller = controller
        self.nombreVote = 0
        self.dernier_vote = "sfsff"

        self.nb_choix1 = 0
        self.nb_choix2 = 0
        self.nb_choix3 = 0
        self.nb_choix4 = 0


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")

            self.client.subscribe(self.topic)

            self.client.subscribe(self.TOPIC_VOTES)

        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        if msg.topic == self.topic:
            vote_recu = msg.payload.decode()
            self.dernier_vote = (f"Message reçu sur {msg.topic} : {vote_recu}")
            print(self.dernier_vote)      

    def connecter(self):
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_start()

    def deconnecter(self):
        self.client.disconnect()
        self.client.loop_stop()

    def envoyerQuestion(self, question, choix):
        message = {"question": question, "choix": choix}
        self.client.publish(self.TOPIC_QUESTION, json.dumps(message, ensure_ascii=False), retain=True)

    def lireVote(self):
        return self.dernier_vote
    
