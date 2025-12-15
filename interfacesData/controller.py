from mqttServer import MqttServer
from interfaceData import InterfaceData
import time
import datetime

class Controller :

    def __init__(self):
        self.interface_data = InterfaceData()
        self.id_statistiques = self.interface_data.obtenir_derniere_stat()
        self.id_question = self.interface_data.obtenir_derniere_question()
        self.mqtt = MqttServer(self.id_statistiques, self.interface_data)
        self.mqtt.connecter_mqtt()
        self.date_ajd = datetime.date.today()


    def enregistrer_vote(self, date, choix, idUser):
        self.interface_data.Ajouter_Vote(idUser, choix, date, self.id_statistiques)
        print("Vote enregistré")

    def enregistrer_question(self, question, listechoix):
        self.id_question = self.interface_data.Ajouter_question(question, listechoix)
        print("question enregistré")
        # mettre à jour la statistique en cours
        self.id_question = self.interface_data.obtenir_derniere_question()
        self.interface_data.mettre_a_jour_question_stat(self.id_statistiques, self.id_question)


    
    def creer_statistique(self,date):
        self.id_question = self.interface_data.obtenir_derniere_question()
        self.interface_data.ajouter_stat(date, self.id_question)
        self.id_statistiques = self.interface_data.obtenir_derniere_stat()

        print("stats creer")

    def calculer_Statistiques(self):
        
        liste_vote = self.interface_data.Obtenir_Vote(self.date_ajd)

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

        self.interface_data.modifier_stat(self.date_ajd, total_choix1, total_choix2, total_choix3, total_choix4, total_vote)
        stats_mqtt = {'stats' : [total_choix1, total_choix2, total_choix3, total_choix4]}
        self.mqtt.EnvoyerStats(stats_mqtt)

    def boucle(self):
        

        while True:
            time.sleep(1)
            choix_du_chef = input("1 pour creér et 2 pour calculer :")
            #si il est 8h00 alors créer statistique
            if choix_du_chef =="1":
                self.date_ajd = datetime.date.today()
                self.creer_statistique(self.date_ajd)

            #si il est 14h00 alors créer statistique
            elif choix_du_chef == "2":
                self.calculer_Statistiques()
                


controller = Controller()

controller.boucle()