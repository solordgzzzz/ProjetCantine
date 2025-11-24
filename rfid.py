
class RFID :

    def __init__(self):
        print("Activation du lecteur RFID")


    def lireRfid(self):
        """Méthode qui permet de faire la lecture du badge
        Elle retourne l'id du badge"""
        
        badge_id = input("Lecture du badge : ")
        
        return badge_id