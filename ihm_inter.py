import tkinter as tk

class IHM:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Système de Vote RFID")

        self.question_label = tk.Label(self.root, text="", font=('Arial', 16, 'bold'))
        self.question_label.pack(pady=20)

        self.choix_frame = tk.Frame(self.root)
        self.choix_frame.pack(pady=10)

        self.msg_label = tk.Label(self.root, text="", font=('Arial', 12), fg="green")
        self.msg_label.pack(pady=20)

    def demander_choix(self, question, listeChoix):
        self.question_label.config(text=question)
        for widget in self.choix_frame.winfo_children():
            widget.destroy()

        for idx, choix in enumerate(listeChoix):
            b = tk.Button(self.choix_frame, text=choix, width=25,
                          command=lambda i=idx+1: self.on_choix(i))
            b.pack(pady=5)

    def on_choix(self, choix):
        # Transmet le choix au contrôleur
        self.controller.choix_fait(choix)

    def afficher_message(self, message):
        self.msg_label.config(text=message)

    def demarrer(self):
        self.root.mainloop()
