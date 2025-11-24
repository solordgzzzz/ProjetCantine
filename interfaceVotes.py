import random, json
from paho.mqtt import client as mqtt_client

class InterfaceVotes:

    BROKER = '192.168.190.17'
    PORT = 1883
    TOPIC_QUESTION = 'cantine/question'
    USERNAME = "crdg"
    PASSWORD = "crdg*123"

    def __init__(self, num_pupitre,controller):
        #création du topic pour le pupitre
        self.topic = f'cantine/pupitre/{num_pupitre}/vote'
       
        # generate client ID with pub prefix randomly
        self.client_id = f'Cantine-{random.randint(0, 1000)}'
        
        #création du client
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1,client_id=self.client_id)
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)
        
        #création des liens de fonction callback
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.controller = controller


    def on_connect(self,client, userdata, flags, rc):
        if rc == 0:
            self.client.subscribe(self.TOPIC_QUESTION)
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self,client, userdata, msg):
        print("messagerecu", msg.topic)
        if msg.topic == self.TOPIC_QUESTION:
            payload = json.loads(msg.payload)
            question = payload['question']
            listeChoix = payload['choix']
            self.controller.modifierQuestion(question,listeChoix)

    def connecter(self):
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_start()

    def deconnecter(self):
        self.client.disconnect()
        self.client.loop_stop()

    def envoyerVote(self, vote):
        #création du message en JSON
        msg = vote.toJson()
        result = self.client.publish(self.topic, msg)
        # result: [0, 1]
        status = result[0]
        
        return status, self.topic, msg



