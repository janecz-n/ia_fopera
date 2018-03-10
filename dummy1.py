#Fantome
from random import randrange, choice
import logger
from list_card import weight_data
from lien_map import passages, pass_ext

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
log = logger.log

def lancer():
    fini = False
    old_question = ""
    manager = Manager()
    infoEndOfPartie = open('./1/infos.txt','r')
    positionForEndOfPartie = 0
    lastInfo = ""
    while len(manager.fantome) <= 0:
        infof = open('./1/infos.txt','r')
        manager.fantome = infof.readline().split(':')[-1].strip()
        log("Fantome : " + manager.fantome)
        infof.close()
    while not fini:
        manager.getGameState()
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
        lastInfos = infoEndOfPartie.readlines()
        for l in lastInfos:
            if "Score final" in l:
                fini = True
            elif not any(w in l for w in ["QUESTION", "REPONSE"]):
                if "NOUVEAU PLACEMENT" in l:
                    manager.movedPersonnage(l)
                # else:
                #     log("Info : " + l)
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
        self.Personnages = {'bleu': {'room': '3', 'suspect': 1}, 'rouge': {'room': '4', 'suspect': 1}, 'marron': {'room': '7', 'suspect': 1},\
                            'violet': {'room': '1', 'suspect': 1}, 'gris': {'room': '6', 'suspect': 1}, 'noir': {'room': '5', 'suspect': 1},\
                            'rose': {'room': '2', 'suspect': 1}, 'blanc': {'room': '0', 'suspect': 1}}
        self.Rooms = {'0':[], '1':[], '2':[], '3':[], '4':[], '5':[], '6':[], '7':[], '8':[], '9':[]}
        self.Cleans = []
        self.FDGameState = open('./1/infos.txt','r')
        self.posFDGameState = 0
        self.fantome = ""
        self.selectedPersonnage = ""
        self.split = True

    def closeFD(self):
        self.FDGameState.close()

    def calcPoint(self):
        suspectAlone = 0
        for r in self.Rooms:
            for p in self.Rooms[r]:
                #is supect
                self.Rooms[r][p]
            #How many in this room
            len(self.Rooms[r])
        roomFantome = ""
        try:
            log ()
            log ("ppl in fantome room: " + str(len(self.Rooms[self.Personnages[self.fantome]["room"]])))
        except:
            pass
        # for p in self.Personnages:
        #     if p["color"] == self.fantome:
        #         roomFantome = p["room"]
        # log (ENDC)
        # log (rooms)
        # log ("len: " + str(len(rooms[roomFantome])))
        # log (GREEN)

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
        self.Rooms = {'0':{}, '1':{}, '2':{}, '3':{}, '4':{}, '5':{}, '6':{}, '7':{}, '8':{}, '9':{}}
        self.Cleans = []
        for p in personnages.split("  "):
            #pI = personnage Information
            pI = p.strip().split('-')
            self.Personnages[pI[0]]["room"] = pI[1]
            self.Personnages[pI[0]]["suspect"] = 1 if pI[2] == "suspect" else 0
            self.Rooms[pI[1]][pI[0]] = self.Personnages[pI[0]]["suspect"]
            if pI[2] == "clean":
                self.Cleans.append(pI[0])
        log ("Perso: ")
        log(self.Personnages)
        log ("Rooms: ")
        log(self.Rooms)
        log ("Clean: ")
        log(self.Cleans)

    #Fonction qui determine si les personnages doivent se regrouper
    #ou se separer
    def shouldISplit(self):
        nbSuspect = 0
        nbSuspectAlone = 0
        for r in self.Rooms:
            for p in self.Rooms[r]:
                #is supect
                if self.Rooms[r][p] > 0:
                    nbSuspect += 1
                    if len(self.Rooms[r]) == 1:
                        nbSuspectAlone += 1
        log ("nbSuspect: " + str(nbSuspect))
        log ("nbSuspectAlone: " + str(nbSuspectAlone))
        if nbSuspectAlone >= 4 and len(self.Rooms[self.Personnages[self.fantome]["room"]]) == 1:
            return (True)
        return (False)

    #Selectionne une tuile en fonction de:
    #Si le fantome est tout seul ou non
    #Si la tuile est suspect
    #Si le pouvoir de la tuile a un poids plus eleve
    def selectTuile(self, question):
        self.calcPoint()
        tuiles = question.split('[')[1].split(']')[0].split(',')
        #isFantomAlone = True if len(self.Rooms[self.Personnages[self.fantome]["room"]]) == 1 else False
        isFantomAlone = self.shouldISplit()
        self.split = isFantomAlone
        #Don t waste time if only one available
        if len(tuiles) == 1:
            self.selectedPersonnage = tuiles[0].strip().split('-')[0]
            return str(0)
        posInQuestion = 0
        persoPossibility = {}
        heaviestCard_pos = 0
        heaviestCard_weight = 0
        for t in tuiles:
            #pI = personnage Information
            pI = t.strip().split('-')
            room = self.Personnages[pI[0]]["room"]
            log ("Current (" + pI[0] + ") " + pI[2] + "; room: " + room + "; ppl in room: " + str(len(self.Rooms[room])))
            zePassage = passages
            if pI[0] == "rose":
                zePassage = pass_ext
            for p in zePassage[int(room)]:
                #Locked passage
                if room in self.Lock and str(p) in self.Lock:
                    log  ("Passage " + room + " to " + str(p) + " is locked..")
                    continue
                sizeOfRoomAfterMove = len(self.Rooms[str(p)])
                if str(p) in question:
                    sizeOfRoomAfterMove -= 1
                log ("ppl in room annex (" + str(p) + ") : " + str(len(self.Rooms[str(p)])) + " after move: " + str(sizeOfRoomAfterMove))
                if isFantomAlone and (sizeOfRoomAfterMove == 0 or self.Ombre == p):
                    persoPossibility[posInQuestion] = pI[0]
                    continue
                elif not isFantomAlone and sizeOfRoomAfterMove > 0:
                    persoPossibility[posInQuestion] = pI[0]
                    continue
            if weight_data[pI[0]] > heaviestCard_weight:
                heaviestCard_pos = posInQuestion
                heaviestCard_weight = weight_data[pI[0]]
                self.selectedPersonnage = pI[0]
            posInQuestion += 1
        log (persoPossibility)
        if len(persoPossibility) > 0:
            heaviestCard_weight = 0
            for p in persoPossibility:
                bonus = int(self.Personnages[persoPossibility[p]]["suspect"]) * 10
                if bonus + weight_data[persoPossibility[p]] > heaviestCard_weight:
                    heaviestCard_pos = p
                    heaviestCard_weight = bonus + weight_data[persoPossibility[p]]
                    self.selectedPersonnage = persoPossibility[p]
        return str(heaviestCard_pos)

    def usePositionPower(self, question):
        posDispo = question.split('{')[1].split('}')[0].split(',')
        pos = []
        for p in posDispo:
            pos.append(int(p.strip()))
        return choice(pos)

    #Selectionne le lieu ou se deplacer en fct de si le fantome est tout seul ou non
    def movePersonnage(self, question):
        posDispo = question.split('{')[1].split('}')[0].split(',')
        pos = 0
        posValue = 10
        if self.split == True:
            posValue = 0
        for p in posDispo:
            cleanPos = p.strip()
            if self.split is True:
                if len(self.Rooms[cleanPos]) == 0 or int(cleanPos) == self.Ombre:
                    pos = cleanPos
                    break
                if len(self.Rooms[cleanPos]) > posValue:
                    posValue = len(self.Rooms[cleanPos])
                    pos = cleanPos
            elif self.split is False:
                if len(self.Rooms[cleanPos]) > 0 and len(self.Rooms[cleanPos]) < posValue:
                    pos = cleanPos
                    posValue = len(self.Rooms[cleanPos])
            else:
                pos = cleanPos
        return pos

    def selectQuestion(self, question):
        if "Tuiles disponibles :" in question:
            return str(self.selectTuile(question))
        elif "Voulez-vous activer le pouvoir" in question:
            return str(1)
        elif ", positions disponibles" in question:
            return str(self.usePositionPower(question))
        elif "positions disponibles" in question:
            return str(self.movePersonnage(question))
        elif "Avec quelle couleur échanger" in question:
            return str(self.useSwitchPower())
        elif "Quelle salle obscurcir ?" in question:
            return str(self.roomBlacked())
        elif "Quelle salle bloquer ?" in question:
            return str(2)
        elif "Quelle sortie ?" in question:
            return str(self.usePositionPower(question))
        else:
            return str(0)

    def movedPersonnage(self, info):
        try:
            info = info.split(' : ')[1]
            #pI = personnage Information
            pI = info.strip().split('-')
            del self.Rooms[self.Personnages[pI[0]]["room"]][pI[0]]
            self.Personnages[pI[0]]["room"] = pI[1]
            self.Personnages[pI[0]]["suspect"] = 1 if pI[2] == "suspect" else 0
            self.Rooms[pI[1]][pI[0]] = self.Personnages[pI[0]]["suspect"]
        except:
            pass

    def roomBlacked(self):
        #Si fantome tout seul
        #Return la case avec le plus de suspect
        if len(self.Rooms[self.Personnages[self.fantome]["room"]]) == 1:
            nbRoom = 0
            maxSuspectInRoom = 0
            for r in self.Rooms:
                suspectInRoom = 0
                for p in self.Rooms[r]:
                    #is suspect
                    if self.Rooms[r][p] > 0:
                        suspectInRoom += 1
                if suspectInRoom > maxSuspectInRoom:
                    nbRoom = r
                    maxSuspectInRoom = suspectInRoom
            #Si tout les suspects solo alors return fantome
            if maxSuspectInRoom == 1:
                return (self.Personnages[self.fantome]["room"])
            return (nbRoom)
        #Si le fantome n est pas tout seul et qu il devrait
        #return la case du fantome
        elif self.split == True or len(self.Rooms[self.Personnages[self.fantome]["room"]]) > 1:
            return (self.Personnages[self.fantome]["room"])
        #Si les suspect ne doivent pas se split et que le fantome n est pas tout seul
        #return une case aleatoire sans suspect
        else:
            nbRoom = 0
            maxNoneSuspectInRoom = 0
            for r in self.Rooms:
                noneSuspectInRoom = 0
                for p in self.Rooms[r]:
                    #is not suspect
                    if self.Rooms[r][p] == 0:
                        noneSuspectInRoom += 1
                    else:
                        continue
                if noneSuspectInRoom > maxNoneSuspectInRoom:
                    nbRoom = r
                    maxNoneSuspectInRoom = noneSuspectInRoom
            return (nbRoom)

    #Utilise le pouvoir violet
    def useSwitchPower(self):
        #Sauve le fantome si il doit etre seul
        if len(self.Rooms[self.Personnages["violet"]["room"]]) == 1 and self.split == True and len(self.Rooms[self.Personnages[self.fantome]["room"]]) > 1:
            return (self.fantome)
        #Sauve le fantome si il doit etre en groupe
        if len(self.Rooms[self.Personnages["violet"]["room"]]) > 1 and self.split == False and len(self.Rooms[self.Personnages[self.fantome]["room"]]) == 1:
            return (self.fantome)
        if self.Personnages["violet"]["suspect"] == 1:
            #Sauve le violet si il doit etre seul
            if len(self.Rooms[self.Personnages["violet"]["room"]]) > 1 and self.split == True:
                for r in self.Rooms:
                    if r != self.Personnages["violet"]["room"]:
                        if len(self.Rooms[r]) == 1:
                            for p in self.Rooms[r]:
                                #is not suspect
                                if self.Rooms[r][p] == 0:
                                    return (p)
            #Sauve le violet si il doit etre en groupe
            if len(self.Rooms[self.Personnages["violet"]["room"]]) == 1 and self.split == False:
                colorOfNoneSuspect = ""
                colorToKeep = ""
                maxNoneSuspectInRoom = 0
                for r in self.Rooms:
                    noneSuspectInRoom = 0
                    if r != self.Personnages["violet"]["room"]:
                        if len(self.Rooms[r]) > 1:
                            for p in self.Rooms[r]:
                                #is not suspect
                                if self.Rooms[r][p] == 0:
                                    noneSuspectInRoom += 1
                                    colorOfNoneSuspect = p
                        if noneSuspectInRoom > maxNoneSuspectInRoom:
                            colorToKeep = colorOfNoneSuspect
                            maxNoneSuspectInRoom = noneSuspectInRoom
                if len(colorToKeep):
                    return (colorToKeep)
        else:
            #Sauve un suspect si il doit etre seul
            if len(self.Rooms[self.Personnages["violet"]["room"]]) == 1 and self.split == True:
                colorOfSuspect = ""
                colorToKeep = ""
                maxSuspectInRoom = 0
                for r in self.Rooms:
                    suspectInRoom = 0
                    if r != self.Personnages["violet"]["room"]:
                        if len(self.Rooms[r]) > 1:
                            for p in self.Rooms[r]:
                                #is suspect
                                if self.Rooms[r][p] > 0:
                                    suspectInRoom += 1
                                    colorOfSuspect = p
                            if suspectInRoom > maxSuspectInRoom:
                                colorToKeep = colorOfSuspect
                                maxSuspectInRoom = suspectInRoom
                if len(colorToKeep):
                    return (colorToKeep)
                #Sauve un suspect si il doit etre en groupe
                if len(self.Rooms[self.Personnages["violet"]["room"]]) > 1 and self.split == False:
                    for r in self.Rooms:
                        if r != self.Personnages["violet"]["room"]:
                            if len(self.Rooms[r]) == 1:
                                for p in self.Rooms[r]:
                                    #is suspect
                                    if self.Rooms[r][p] == 1:
                                        return (p)
        if self.fantome != "bleu":
            return ("bleu")
        return ("marron")
