from mqttServer import MqttServer
from interfaceData import InterfaceData
import time
import datetime

class Controller :

    def __init__(self):
        self.interface_data = InterfaceData()
        self.id_statistiques = 29
        self.id_question = 5
        self.mqtt = MqttServer(self.id_statistiques, self.interface_data)
        self.mqtt.connecter_mqtt()
        self.date_ajd = datetime.date.today()
        self.datejour = "2025-12-12"


    def enregistrer_vote(self, date, choix, idUser):
        self.interface_data.Ajouter_Vote(idUser, choix, date, self.id_statistiques)
        print("Vote enregistré")

    def enregistrer_question(self, question, listechoix):
        self.interface_data.Ajouter_question(question, listechoix)
        print("question enregistré")

    
    def creer_statistique(self,date, idQuestion):
        self.interface_data.ajouter_stat(date, idQuestion)
        print("stats creer")

    def calculer_Statistiques(self, datejour):
        
        liste_vote = self.interface_data.Obtenir_Vote(self.datejour)

        total_choix1 = 0
        total_choix2 = 0
        total_choix3 = 0
        total_choix4 = 0

        #boucle pour calculer les statistiques
        for vote in liste_vote:
            choix = vote[2]
            if choix == 1:
                total_choix1 += 1
            elif choix == 2:
                total_choix2 += 1
            elif choix == 3:
                total_choix3 += 1
            elif choix == 4:
                total_choix4 += 1

        total_vote = total_choix1 + total_choix2 + total_choix3 + total_choix4

        stats = (self.id_statistiques, total_choix1, total_choix2, total_choix3, total_choix4, total_vote)

        self.interface_data.modifier_stat(self.datejour, total_choix1, total_choix2, total_choix3, total_choix4, total_vote)

    def boucle(self):
        

        while True:
            time.sleep(1)
            choix_du_chef = input("1 pour creér et 2 pour calculer :")
            #si il est 8h00 alors créer statistique
            if choix_du_chef =="1":
                self.creer_statistique(self.date_ajd, self.id_question)

            #si il est 14h00 alors créer statistique
            elif choix_du_chef == "2":
                datejour = self.datejour
                self.calculer_Statistiques(datejour)


controller = Controller()

controller.boucle()