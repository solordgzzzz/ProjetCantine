import random, json
from paho.mqtt import client as mqtt_client
from vote import Vote


class appServeur:

    BROKER = '192.168.190.15'
    PORT = 1883
    TOPIC_VOTES = 'cantine/stats_votes'
    USERNAME = "crdg"
    PASSWORD = "crdg*123"

    def __init__(self,controller):
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
        self.dernier_vote = ""


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")

            self.client.subscribe(self.topic)

        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        vote_recu_str = msg.payload.decode()
        print(f"Message reçu sur {msg.topic} : {vote_recu_str}")

        vote_recu = json.loads(vote_recu_str)

        choix = int(vote_recu['choix'])
        

        self.controller.calculer_statistiques(choix)                



    def connecter(self):
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_start()

    def deconnecter(self):
        self.client.disconnect()
        self.client.loop_stop()

    def envoyerStats(self,nb_choix):
        stats = {'stats': nb_choix}
        return self.client.publish(self.TOPIC_VOTES, json.dumps(stats, ensure_ascii=False),qos= 1, retain=True)