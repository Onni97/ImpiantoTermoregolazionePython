from typing import Union
import dbUtils


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
        elif symbol == "True" or symbol == "False":
            output.append(symbol)
        else:
            return -1
        #print("OUTPUT: " + str(output) + "\nOPERATORS: " + str(operators) + "\n\n")
    while len(operators) > 0:
        output.append(operators.pop())

    return output



#restituisce true se l'espressione è verificata
def evaluate(expression: str) -> bool:
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
            value = exec(symbol)
        #print("EXPRESSION: " + str(expression) + "\nSTACK: " + str(stack) + "\n\n")

    return stack.pop()



def check(sensor: int):
    return





##### FUNZIONI DELLE REGOLE #####

#funzioni base per vedere i valori dei sensori, hanno più alias per la comodità dell'utente
def getValue(sensorX: int):
    return dbUtils.getSensorValue(sensorX)
termometro = condizionatore = finestra = getValue



#restituisce true se un sensore rileva l'assenza tra
def absenceBetween(sensorX: int, min: int, max: int):

    return
##########





#infix = " not ( True or ( False or ( True and not True ) ) or False )"
#print("INFIX: %s\n" % infix)
#
#result = evaluate(infix)
#print("Result = " + str(result))