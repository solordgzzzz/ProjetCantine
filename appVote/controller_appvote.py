from appvote import AppVote
from ihm_inter import IHM
import time


class Controller_appvote:

    def __init__(self):

        self.AppVote = AppVote(self)
        self.AppVote.connecter()
        
        self.nb_choix = [0,0,0,0]

    def calculer_statistiques(self, choix):
        self.nb_choix[choix-1] += 1    

        self.AppVote.envoyerStats(self.nb_choix)

app = Controller_appvote()

while True:
    pass