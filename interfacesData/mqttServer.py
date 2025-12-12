import random
import json
import mysql.connector
from paho.mqtt import client as mqtt_client
from datetime import date
import time  
from interfaceData import InterfaceData


class MqttServer:

    BROKER = '192.168.190.15'
    PORT = 1883
    TOPIC_QUESTION = 'cantine/question'
    USERNAME = "crdg"
    PASSWORD = "crdg*123"

    def __init__(self, id_statistiques, interfaceData):
        self.topic = f'cantine/pupitre/1/vote'
        self.client_id = f'Cantine-{random.randint(0, 1000)}'
        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.username_pw_set(self.USERNAME, self.PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.dernier_vote = None
        self.id_statistiques = id_statistiques 
        self.interfaceData = interfaceData

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connecté au broker MQTT !")
            client.subscribe(self.TOPIC_QUESTION)
            client.subscribe(self.topic)
        else:
            print(f"Échec de connexion, code: {rc}")

    def on_message(self, client, userdata, msg):
        if msg.topic == self.topic:
            payload = msg.payload.decode()
            vote_data = json.loads(payload)
            self.dernier_vote = vote_data
            print("Vote reçu:", vote_data)
            self.interfaceData.Ajouter_Vote(vote_data['id_votant'],vote_data['choix'],str(date.today()),self.id_statistiques)

        elif msg.topic == self.TOPIC_QUESTION:
            payload = msg.payload.decode()
            question_data = json.loads(payload)
            print("question recu", question_data)
            self.interfaceData.Ajouter_question(question_data['question'],question_data['choix'][0],question_data['choix'][1],question_data['choix'][2],question_data['choix'][3])   

    # Méthodes MQTT
    def connecter_mqtt(self):
        self.client.connect(self.BROKER, self.PORT)
        self.client.loop_start()

    def deconnecter_mqtt(self):
        self.client.disconnect()
        self.client.loop_stop()