#per questa implementazione ipotizzo che non ci possano essere sensori senza un ufficio

from datetime import datetime
from typing import Union
import dbUtils

SEASON = "Summer"


def shuntingYardAlgorithm(rule: str) -> Union[list, int]:
    rule = rule.split()
    operators = []
    output = []

    for symbol in rule:
        if symbol == "not":
            operators.append("not")
        elif symbol == "and":
            while len(operators) != 0 and ((operators[-1] != "not") and operators[-1] != "("):
                output.append(operators.pop())
            operators.append("and")
        elif symbol == "or":
            while len(operators) != 0 and ((operators[-1] != "not" or operators[-1] != "and") and operators[-1] != "("):
                output.append(operators.pop())
            operators.append("or")
        elif symbol == "(":
            operators.append("(")
        elif symbol == ")":
            while operators[-1] != "(":
                output.append(operators.pop())
            operators.pop()
        else:
            output.append(symbol)
        #print("OUTPUT: " + str(output) + "\nOPERATORS: " + str(operators) + "\n\n")
    while len(operators) > 0:
        output.append(operators.pop())

    return output



#restituisce true se l'espressione è verificata
def evaluate(expression: str, sensoreX: int, ufficioX: int) -> bool:
    expression = shuntingYardAlgorithm(expression)
    stack = []
    expression.reverse()

    #print("EXPRESSION: " + str(expression) + "\nSTACK: " + str(stack) + "\n\n")
    while len(expression) > 0:
        symbol = expression.pop()
        if symbol == "not":
            stack.append(not stack.pop())
        elif symbol == "and":
            op1 = stack.pop()
            op2 = stack.pop()
            stack.append(op1 and op2)
        elif symbol == "or":
            op1 = stack.pop()
            op2 = stack.pop()
            stack.append(op1 or op2)
        else:
            value = eval(symbol)
            stack.append(value)
        #print("EXPRESSION: " + str(expression) + "\nSTACK: " + str(stack) + "\n\n")
    return stack.pop()



#in base al sensore passato esegue i controlli sulle regole relative
def check(sensor: int):

    office = dbUtils.getOfficeBySensor(sensor)
    rules = dbUtils.getRuleBySensor(sensor)
    for rule in rules:
        checkRule(rule, sensor, office)
    return



#controlla la singola regola
def checkRule(rule: list, sensoreX: int, ufficioX: int):
    if evaluate(rule[0], sensoreX, ufficioX):
        evaluate(rule[1], sensoreX, ufficioX)
    return





##### FUNZIONI DELLE REGOLE #####

#restituisce True se il condizionatore passato è acceso, False altrimenti
def condizionatore(sensoreX: int):
    if dbUtils.getSensorValue(sensoreX) == 1:
        return True
    else:
        return False

finestra = condizionatore



#restituisce True se un sensore rileva l'assenza tra un certo intervallo (in minuti), False altrimenti
def assenzaTra(sensoreX: int, min: int, max: int):
    value = str(dbUtils.getSensorValue(sensoreX))
    time = datetime(int(value[0:4]), int(value[4:6]), int(value[6:8]), int(value[8:10]), int(value[10:12]), int(value[12:14]))
    absence = datetime.now() - time
    absence = absence.days * 86400 + absence.seconds

    if min*60 > absence > max*60:
        return True
    else:
        return False



#restituisce True se l'ufficio passato ha tutte le finestre chiuse, False altrimenti
def finestreUfficioAperte(ufficioX: int):
    return  dbUtils.checkIfOfficeHasOpenWindows(ufficioX)



#restituisce True se in un ufficio l'assenza è tra un certo intervallo (in minuti), False altrimenti
def assenzaTraInUfficio(ufficioX: int, min: int, max: int):
    value = str(dbUtils.getLastPresenceInOffice(ufficioX))
    time = datetime(int(value[0:4]), int(value[4:6]), int(value[6:8]), int(value[8:10]), int(value[10:12]), int(value[12:14]))
    absence = datetime.now() - time
    absence = absence.days * 86400 + absence.seconds

    if min*60 > absence > max*60:
        return True
    else:
        return False



#restituisce True se la temperatura di un ufficio è nel range, False altrimenti
def TemperaturaUfficioInRange(sensoreX: int, error: int):
    value = dbUtils.getSensorValue(sensoreX)
    office = dbUtils.getOfficeBySensor(sensoreX)
    average = dbUtils.getAverageT(office)

    if SEASON == "Summer":
        if value > average+error:
            return False
        else:
            return True
    elif SEASON == "Winter":
        if value < average-error:
            return False
        else:
            return True
    return -1



#aggiunge nelle actionstodo l'accensione dei condizionatori dell'ufficio x
def accendiCondizionatoriUfficio(ufficioX: int):
    conditioneers = dbUtils.getConditioneerOfOffice(ufficioX)
    for conditioneer in conditioneers:
        raspberrys = dbUtils.getRaspberrysForSensor(conditioneer)
        dbUtils.addAction(raspberrys, conditioneer, 1)
    return



#aggiunge nelle actionstodo lo spegnimento dei condizionatori dell'ufficio x
def spegniCondizionatoriUfficio(ufficioX: int):
    conditioneers = dbUtils.getConditioneerOfOffice(ufficioX)
    for conditioneer in conditioneers:
        raspberrys = dbUtils.getRaspberrysForSensor(conditioneer)
        dbUtils.addAction(raspberrys, conditioneer, 1)
    return
##########





#infix = " not ( True or ( False or ( True and not True ) ) or False )"
#print("INFIX: %s\n" % infix)
#
#result = evaluate(infix)
#print("Result = " + str(result))

finestreUfficioAperte(1)