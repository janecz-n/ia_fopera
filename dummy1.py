#Fantome
from random import randrange, choice
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
    fantome = ""
    infoEndOfPartie = open('./1/infos.txt','r')
    positionForEndOfPartie = 0
    while not fini:
        manager.getGameState()
        if len(fantome) < 1:
            infof = open('./1/infos.txt','r')
            fantome = infof.readline().split(':')[-1].strip()
            log("Fantome : " + fantome)
            infof.close()
        qf = open('./1/questions.txt','r')
        question = qf.read().strip()
        qf.close()
        if len(question) > 3 and question != old_question :
            log(GREEN, end='')
            rf = open('./1/reponses.txt','w')
            log("Q: " + question, end=' A: ')
            answer = manager.selectQuestion(question)
            log(answer)
            log(ENDC, end='')
            rf.write(answer)
            rf.close()
            old_question = question
        infoEndOfPartie.seek(positionForEndOfPartie)
        fini = "Score final" in infoEndOfPartie.read()
        positionForEndOfPartie = infoEndOfPartie.tell()
    infoEndOfPartie.close()
    manager.closeFD()

"""
Tuiles disponibles : [bleu-2-suspect, noir-3-suspect, violet-6-suspect, rouge-5-suspect] choisir entre 0 et 3
Voulez-vous activer le pouvoir (0/1) ?
positions disponibles : {1, 3}, choisir la valeur
"""

class Manager:
    def __init__(self):
        self.Tour = 0
        self.Points = 0
        self.Ombre = 0
        self.Lock = 0
        self.Personnages = []
        self.FDGameState = open('./1/infos.txt','r')
        self.posFDGameState = 0

    def closeFD(self):
        self.FDGameState.close()

    def getGameState(self):
        self.FDGameState.seek(self.posFDGameState)
        line = self.FDGameState.readline()
        while line != '' and "Tour:" + str(self.Tour + 1) not in line:
            line = self.FDGameState.readline()
        if line == '':
            return
        state = line.split(',')
        self.Tour = int(state[0].split(':')[1])
        log("Tour:", end='')
        log(self.Tour, end=' ; ')
        self.Points = int(state[1].split(':')[1].split('/')[0])
        log("Points:", end='')
        log(self.Points, end=' ; ')
        self.Ombre = int(state[2].split(':')[1])
        log("Ombre:", end='')
        log(self.Ombre, end=' ; ')
        self.Lock = state[3].split(':')[1] + ', ' + state[4].strip()
        log("Lock:", end='')
        log(self.Lock)
        personnages = self.FDGameState.readline()
        self.posFDGameState = self.FDGameState.tell()
        self.Personnages = []
        for p in personnages.split("  "):
            personnageInfos = p.strip().split('-')
            perso = {}
            perso["color"] = personnageInfos[0]
            perso["room"] = personnageInfos[1]
            perso["suspect"] = 1 if personnageInfos[2] == "suspect" else 0
            self.Personnages.append(perso)
        log(self.Personnages)

    def selectTuile(self, question):
        tuiles = question.split('[')[1].split(']')[0].split(',')
        personnages = []
        p = 0
        for t in tuiles:
            personnageInfos = t.strip().split('-')
            perso = {}
            perso["pos"] = p
            p += 1
            perso["color"] = personnageInfos[0]
            perso["room"] = personnageInfos[1]
            perso["suspect"] = 1 if personnageInfos[2] == "suspect" else 0
            personnages.append(perso)
        return str(0)

    def selectPosition(self, question):
        posDispo = question.split('{')[1].split('}')[0].split(',')
        pos = []
        for p in posDispo:
            pos.append(int(p.strip()))
        return choice(pos)

    def selectQuestion(self, question):
        if "Tuiles disponibles :" in question:
            return str(self.selectTuile(question))
        elif "Voulez-vous activer le pouvoir" in question:
            return str(1)
        elif ", positions disponibles" in question:
            return str(self.selectPosition(question))
        elif "positions disponibles" in question:
            return str(self.selectPosition(question))
        elif "Avec quelle couleur échanger" in question:
            return "rose"
        elif "Quelle salle obscurcir ?" in question:
            return str(2)
        elif "Quelle salle bloquer ?" in question:
            return str(2)
        elif "Quelle sortie ?" in question:
            return str(self.selectPosition(question))
        else:
            return str(0)
