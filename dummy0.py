#Enqueteur
from random import randrange
import logger

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
log = logger.log

def lancer():
    fini = False
    old_question = ""
    manager = Manager()
    while not fini:
        qf = open('./0/questions.txt','r')
        question = qf.read().strip()
        qf.close()
        if len(question) > 3 and question != old_question :
            log (YELLOW, end='')
            rf = open('./0/reponses.txt','w')
            log ("Q: " + question, end=' A: ')
            answer = manager.selectQuestion(question)
            log (answer)
            log (ENDC, end='')
            rf.write(answer)
            rf.close()
            old_question = question
        infof = open('./0/infos.txt','r')
        fini = "Score final" in infof.read()
        infof.close()

"""
Tuiles disponibles : [bleu-2-suspect, noir-3-suspect, violet-6-suspect, rouge-5-suspect] choisir entre 0 et 3
Voulez-vous activer le pouvoir (0/1) ?
positions disponibles : {1, 3}, choisir la valeur

"""

class Manager:
    def selectTuile(self, question):
        tuiles = question.split('[')[1].split(']')[0].split(',')
        personnages = []
        for t in tuiles:
            personnageInfos = t.strip().split('-')
            perso = {}
            perso["color"] = personnageInfos[0]
            perso["room"] = personnageInfos[1]
            perso["suspect"] = 1 if personnageInfos[2] == "suspect" else 0
            personnages.append(perso)
        return str(0)

    def selectQuestion(self, question):
        if "Tuiles disponibles :" in question:
            return str(self.selectTuile(question))
        elif "Voulez-vous activer le pouvoir" in question:
            return str(1)
        elif "positions disponibles" in question:
            return str(2)
        else:
            return str(0)
