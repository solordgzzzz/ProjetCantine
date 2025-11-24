from interfaceVotes import InterfaceVotes
from vote import Vote
from rfid2 import RFID2
from ihmConsole import IHM
import time
from dataTestVotes import dataTestVotes

class Controller:
    def __init__(self):
        self.question = "Comment avez vous trouvé le repas ?"
        self.listeChoix = ['Bof','Ca va','Bon','Top']
        self.rfid =RFID2()
        self.ihm = IHM()
        self.interfaceVotes = InterfaceVotes(1,self)

        self.interfaceVotes.connecter()
    
    def voter(self):
        """Methode permettant de demander le vote et le transmettre"""
        while True:
            id_votant = self.rfid.lireRfid()    #lecture de l'identifiant
            choix = self.ihm.demander_choix(self.question,self.listeChoix)  #demande du choix
            vote = Vote(id_votant, choix)    #création du vote
            status = self.interfaceVotes.envoyerVote(vote)   #envoyer vote
            if status[0] == 0:
                self.ihm.afficher_message("Le vote a été transmis")
            else : 
                self.ihm.afficher_message(status)

    def modifierQuestion(self,question,listeChoix):
        """Méthode appelée lorsqu'une question est recue pour la mémoriser"""
        self.question = question
        self.listeChoix = listeChoix
        self.ihm.afficher_message("Une nouvelle question a été recue")



app = Controller()
app.voter()