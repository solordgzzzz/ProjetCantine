from interfaceVotes import InterfaceVotes
from vote import Vote
from rfid import RFID
from ihm_inter import IHM
import time


class Controller_chef:

    def __init__(self):
        self.question = "Comment avez vous trouvé le repas ?"
        self.listeChoix = ['Éclaté', 'bof', 'Bon', 'Excellent']

        self.rfid = RFID()
        self.ihm = IHM(self)

        self.interfaceVotes = InterfaceVotes(1, self)
        self.interfaceVotes.connecter()

        # affichage initial
        self.ihm.demander_choix(self.question, self.listeChoix)

    def modifierQuestion(self, question, listeChoix):
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.demander_choix(self.question, self.listeChoix)
        self.ihm.afficher_message("Une nouvelle question a été reçue!")
        self.interfaceVotes.envoyerQuestion(self.question, self.listeChoix)

    def visualiserVotes(self):
        pass


app = Controller_chef()
app.modifierQuestion()