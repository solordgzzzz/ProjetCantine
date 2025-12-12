import random
import json
import mysql.connector
from paho.mqtt import client as mqtt_client
from datetime import date
import time  

# Connexion MySQL
mydb = mysql.connector.connect(
    host="192.168.190.15",
    user="root",
    password="root",
    port="3310",
    database="bdd_cantine"
)

class InterfaceData:


    def Ajouter_Vote(self, identifiant, choix_vote, date, idstatistiques):
        mycursor = mydb.cursor()
        sql = "INSERT INTO vote (identifiant, choix_vote, date, idstatistiques) VALUES (%s, %s, %s, %s)"
        val = (identifiant, choix_vote, date, idstatistiques)
        mycursor.execute(sql, val) 
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")

    def Modifier_Vote(self, identifiant, choix_vote):
        mycursor = mydb.cursor()
        sql = f"UPDATE vote SET choix_vote = {choix_vote} WHERE identifiant = {identifiant}"
        mycursor.execute(sql)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")

    def Obtenir_Vote(self, date):
        mycursor = mydb.cursor()
        sql = f"SELECT * FROM vote WHERE date = %s"
        val = [date]
        mycursor.execute(sql, val)
        message = mycursor.fetchall()
        for x in message:
            print(x)
        return message
    
    def ajouter_stat(self, date, idQuestion):
        mycursor = mydb.cursor()
        sql = "INSERT INTO statistiques (date,idquestion) VALUES (%s, %s)"
        val = (date, idQuestion)
        try:
            mycursor.execute(sql, val)
            mydb.commit()
            print("Tuple ajouté")
        except mysql.connector.IntegrityError as err:
            print("Error: {}".format(err))

    def modifier_stat(self, date, stat_choix1, stat_choix2, stat_choix3, stat_choix4, nombre_vote):
        mycursor = mydb.cursor()
        sql = """
        UPDATE statistiques
        SET stat_choix1 = %s,
            stat_choix2 = %s,
            stat_choix3 = %s,
            stat_choix4 = %s,
            nombre_vote = %s
        WHERE date = %s
        """
        val = (stat_choix1, stat_choix2, stat_choix3, stat_choix4, nombre_vote, date)
        try:
            mycursor.execute(sql, val)
            mydb.commit()
            if mycursor.rowcount == 1:
                print(f"Statistiques de l'ID {date} mises à jour avec succès.")
            else:
                print(f"Aucune ligne mise à jour pour l'ID {date}.")
        except mysql.connector.Error as err:
            print(f"Erreur lors de la mise à jour : {err}")

    def Ajouter_question(self, question, choix1, choix2, choix3, choix4):
        mycursor = mydb.cursor()
        sql = "INSERT INTO question (question, choix1, choix2, choix3 , choix4) VALUES (%s, %s, %s, %s , %s)"
        val = (question, choix1, choix2, choix3 , choix4)
        mycursor.execute(sql, val) 
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")
