from interfaceVotes import InterfaceVotes
from vote import Vote
from rfid2 import RFID2
from ihm_inter import IHM
import time


class Controller:
    def __init__(self):
        self.question = "Comment avez vous trouvé le repas ?"
        self.listeChoix = ['Éclaté','bof','Bon','Excellent']
        self.rfid = RFID2()
        self.ihm = IHM(self)  # Passe le controller à IHM
        self.interfaceVotes = InterfaceVotes(1, self)
        self.interfaceVotes.connecter()
        # Pour l'affichage initial
        self.ihm.demander_choix(self.question, self.listeChoix)

    def voter(self):
        # Lance la boucle principale de Tkinter
        self.id_votant = None
        self.demander_badge()
        self.ihm.demarrer()

    def demander_badge(self):
        self.ihm.afficher_message("Veuillez scanner votre badge RFID")
        # Lance la lecture RFID dans un thread si besoin
        import threading
        threading.Thread(target=self.lire_rfid).start()

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
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Une nouvelle question a été reçue!")

        # IMPORTANT -> envoyer MQTT question + choix
        self.interfaceVotes.envoyerQuestion(self.question, self.listeChoix)


app = Controller()
app.voter()