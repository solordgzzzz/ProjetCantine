
class Vote:

    def __init__(self, id_votant:int, choix:int=0):
        self.id_votant = id_votant
        self.choix = choix

    def changerChoix(self, choix:int):
        self.choix = choix

    def toJson(self):
        return f"'id_votant':{self.id_votant}, 'choix':{self.choix}"
    
    