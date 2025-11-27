import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

class RFID2 :

    def __init__(self):
        print("Activation du lecteur RFID")

    def lireRfid(self):
        """Méthode qui permet de faire la lecture du badge
        Elle retourne l'id du badge"""
        print("Place votre badge RFID ou votre carte")
        badge_id, text = reader.read()
        print(badge_id)

        return badge_id