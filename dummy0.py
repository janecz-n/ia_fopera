#Enqueteur
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
    manager.closeFD()

"""
Tuiles disponibles : [bleu-2-suspect, noir-3-suspect, violet-6-suspect, rouge-5-suspect] choisir entre 0 et 3
Voulez-vous activer le pouvoir (0/1) ?
positions disponibles : {1, 3}, choisir la valeur

"""

class Manager:
    def __init__(self):
        self.power = {'violet':7, 'rouge':8, 'blanc':4, 'bleu':1, 'gris':6, 'rose':5, 'marron':2, 'noir':3}
        self.suspects_per_room = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0}
        self.perso_per_room = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0}
        self.suspects_accompagnes = 0
        self.suspects_seuls = 0
        self.Tour = 0
        self.Points = 0
        self.Ombre = 0
        self.Lock = 0
        self.Personnages = []
        self.current = {}
        self.FDGameState = open('./0/infos.txt','r')
        self.posFDGameState = 0
        self.pouvoir = 0

    def closeFD(self):
        self.FDGameState.close()

    def getGameState(self):
        self.FDGameState.seek(self.posFDGameState)
        line = self.FDGameState.readline()
        while line != '' and "Tour:" + str(self.Tour + 1) not in line:
            line = self.FDGameState.readline()
        if line == '':
            return
        self.suspects_per_room = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0}
        self.perso_per_room = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0}
        self.suspects_accompagnes = 0
        self.suspects_seuls = 0
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
        for p in self.Personnages:
            if p["suspect"] == 1:
                self.suspects_per_room[p["room"]] += 1
            self.perso_per_room[p["room"]] += 1
        for p in self.perso_per_room:
            if self.perso_per_room[p] == 1 and self.suspects_per_room[p] == 1:
                self.suspects_seuls += 1
            elif self.perso_per_room[p] > 1 and self.suspects_per_room[p] >= 1:
                self.suspects_accompagnes += self.suspects_per_room[p]
        log(self.Personnages)

    def is_alone(self, room):
        if self.perso_per_room[room] > 1:
            return False
        return True

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
        weight = {}
        for p in personnages:
            sus = p["suspect"] + 1
            weight[p["color"]] = sus * 1 + self.power[p["color"]]
        coul = str(max(weight, key=weight.get))
        i = 0
        for c in personnages:
            if c["color"] == coul:
                self.current = personnages[i]
                self.pouvoir = 0
                return str(i)
            i += 1
        return str(0)

    def accompagner(self, pos, alone):
        if self.current["suspect"] == 1:
            rooms_perso = []
            for key, value in self.perso_per_room.items():
                if value > 0:
                    rooms_perso.append(int(key))
            sec = [x for x in pos if x in rooms_perso]
            if len(sec) > 0:
                p = choice(sec)
                if alone:
                    self.suspects_accompagnes += 1
                    self.suspects_seuls -= 1
                return p
            p = choice(pos)
            if self.current['color'] == 'noir':
                self.pouvoir = 1
            return p
        else:
            rooms_suspects = []
            for key, value in self.suspects_per_room.items():
                if value > 0:
                    rooms_suspects.append(int(key))
            sec = [x for x in pos if x in rooms_suspects]
            if len(sec) > 0:
                p = choice(sec)
                return p
            p = choice(pos)
            return p

    def isoler(self, pos, alone):
        if self.current["suspect"] == 1:
            rooms_empty = []
            for key, value in self.perso_per_room.items():
                if value == 0:
                    rooms_empty.append(int(key))
            sec = [x for x in pos if x in rooms_empty]
            if len(sec) > 0:
                p = choice(sec)
                if not alone:
                    self.suspects_accompagnes -= 1
                    self.suspects_seuls += 1
                return p
            p = choice(pos)
            if self.current['color'] == 'blanc':
                self.pouvoir = 1
            return p
        else:
            rooms_empty = []
            for key, value in self.perso_per_room.items():
                if value == 0:
                    rooms_empty.append(int(key))
            sec = [x for x in pos if x in rooms_empty]
            if len(sec) > 0:
                p = choice(sec)
                return p
            p = choice(pos)
            return p

    def eteindre(self):
        if self.suspects_accompagnes > self.suspects_seuls:
            rooms_suspects = []
            for key, value in self.suspects_per_room.items():
                if value > 0:
                    rooms_suspects.append(int(key))
            rooms_people = []
            for key, value in self.perso_per_room.items():
                if value > 1:
                    rooms_people.append(int(key))
            sec = [x for x in rooms_suspects if x in rooms_people]
            if len(sec) > 0:
                p = choice(sec)
                return p
        return 0

    def find_suspect_accompagne(self):
        rooms_suspects = []
        for key, value in self.suspects_per_room.items():
            if value > 0:
                rooms_suspects.append(int(key))
        rooms_people = []
        for key, value in self.perso_per_room.items():
            if value > 1:
                rooms_people.append(int(key))
        sec = [x for x in rooms_suspects if x in rooms_people]
        if len(sec) > 0:
            p = choice(sec)
            for s in self.Personnages:
                if s['room'] == p and s['suspect'] == 1 and s['color'] != 'violet':
                    return s['color']
        return "rose"

    def find_isolement(self):
        rooms_people = []
        for key, value in self.perso_per_room.items():
            if value == 1:
                rooms_people.append(int(key))
        if len(rooms_people) > 0:
            p = choice(rooms_people)
            for s in self.Personnages:
                if s['room'] == p and s['color'] != 'violet':
                    return s['color']
        return "rose"

    def find_accompagnement(self):
        rooms_people = []
        for key, value in self.perso_per_room.items():
            if value > 1:
                rooms_people.append(int(key))
        if len(rooms_people) > 0:
            p = choice(rooms_people)
            for s in self.Personnages:
                if s['room'] == p and s['color'] != 'violet':
                    return s['color']
        return "rose"

    def find_suspect_isole(self):
        rooms_suspects = []
        for key, value in self.suspects_per_room.items():
            if value == 1:
                rooms_suspects.append(int(key))
        if len(rooms_suspects) > 0:
            p = choice(rooms_suspects)
            for s in self.Personnages:
                if s['room'] == p and s['suspect'] == 1 and s['color'] != 'violet':
                    return s['color']
        return "rose"

    def change(self):
        suspect = False if self.current['suspect'] == 0 else True
        if self.perso_per_room[self.current['room']] > 1:
            alone = False
        else:
            alone = True
        if alone and self.suspects_accompagnes > self.suspects_seuls:
            return self.find_suspect_accompagne()
        if not alone and self.suspects_accompagnes > self.suspects_seuls and suspect:
            return self.find_isolement()
        if alone and self.suspects_seuls > self.suspects_accompagnes and suspect:
            return self.find_accompagnement()
        if not alone and self.suspects_seuls > self.suspects_accompagnes and not suspect:
            return self.find_suspect_isole()
        return "rose"

    def pouvoir_violet(self):
        suspect = False if self.current['suspect'] == 0 else True
        if self.perso_per_room[self.current['room']] > 1:
            alone = False
        else:
            alone = True
        if alone and self.suspects_accompagnes > self.suspects_seuls:
            return 1
        if not alone and self.suspects_accompagnes > self.suspects_seuls and suspect:
            return 1
        if alone and self.suspects_seuls > self.suspects_accompagnes and suspect:
            return 1
        if not alone and self.suspects_seuls > self.suspects_accompagnes and not suspect:
            return 1
        return 0

    def selectPosition(self, question):
        posDispo = question.split('{')[1].split('}')[0].split(',')
        pos = []
        for p in posDispo:
            pos.append(int(p.strip()))
        is_alone = self.is_alone(self.current["room"])
        if is_alone:
            if self.suspects_seuls - self.suspects_accompagnes > 1:
                return self.accompagner(pos, True)
            else:
                return self.isoler(pos, True)
        else:
            if self.suspects_accompagnes > self.suspects_seuls:
                return self.isoler(pos, False)
            else:
                return self.accompagner(pos, False)
        return choice(pos)

    def selectQuestion(self, question):
        self.getGameState()
        if "Tuiles disponibles :" in question:
            return str(self.selectTuile(question))
        elif "Voulez-vous activer le pouvoir" in question:
            if self.current['color'] == 'gris' or self.current['color'] == 'rouge':
                self.pouvoir = 1
            if self.current['color'] == 'violet':
                return str(self.pouvoir_violet())
            return str(self.pouvoir)
        elif "positions disponibles" in question:
            return str(self.selectPosition(question))
        elif "Avec quelle couleur échanger" in question:
            return str(self.change())
        elif "Quelle salle obscurcir ?" in question:
            return str(self.eteindre())
        elif "Quelle salle bloquer ?" in question:
            return str(2)
        elif "Quelle sortie ?" in question:
            return str(1)
        else:
            return str(0)
