
class IHM:
    def __init__(self):
        print("Alumage de l'interface graphique")

    def demander_choix(self, question,listeChoix):
        print(question)
        for i in range(len(listeChoix)):
            print(f"{i+1}. {listeChoix[i]}")
        
        choix_non_valide = True
        while choix_non_valide :
            try :
                choix = int(input("Faites votre choix : "))
                if choix >=1 and choix<=4:
                    choix_non_valide = False
                else :
                    print(f"Saisissez un nombre entre 1 et {len(listeChoix)}")
            except ValueError:
                print(f"Saisissez un nombre entre 1 et {len(listeChoix)}")
        
        return choix  

    def afficher_message(self, message):
        print(message)
        