import tkinter as tk
from tkinter import messagebox, simpledialog
import random, json
from paho.mqtt import client as mqtt_client

# --- Config MQTT ---
BROKER = '192.168.190.15'
PORT = 1883
TOPIC_QUESTION = 'cantine/question'
USERNAME = "crdg"
PASSWORD = "crdg*123"


class Statistique:
    def __init__(self,controller):

        self.controller = controller
        self.topic_vote = 'cantine/pupitre/+/vote'
        self.topic_stats = 'cantine/stats_votes'
        self.stats = None  # Mis à jour automatiquement
        self.client_id = f'Chef-{random.randint(0, 1000)}'
        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.username_pw_set(USERNAME, PASSWORD)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER, PORT)
        self.client.loop_start()


    @staticmethod
    def calculer_pourcentages(stats):
        if not stats or "stats" not in stats:
            return None

        # Tous les éléments sont des votes par choix
        votes_par_choix = stats["stats"]
        if len(votes_par_choix) < 1:
            return None

        total_votes = sum(votes_par_choix)          # total = somme de tous les choix [web:112][web:117]
        if total_votes == 0:
            return [0.0 for _ in votes_par_choix]

        pourcentages = [(nb_votes / total_votes) * 100 for nb_votes in votes_par_choix]  # [web:26][web:31]
        return pourcentages
