import json
import time
from _ctypes import Union
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread

import jwt
from flask import Flask, request
from werkzeug.exceptions import BadRequestKeyError

import dbUtils, ruleUtils
import smtplib

app = Flask(__name__)

PALACE = 1
HOST = "http://localhost:5001/"
TOKEN_PASSWORD_EMAIL = "trentinodigitale"
TOKEN_PASSWORD_API_MANAGEMENT = "trentinodigitale"
#esempio token = eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.e30.clyIB2MlPp14AnuY-O9jy1VAlJgmVgVUZh5bSCqoK2k
ALGORITHM = "HS256"

SECONDS_BETWEEN_PRESENCE_CHECK = 60
SECONDS_BETWEEN_INACTIVITY_CHECK = 60
INACTIVITY_SECONDS_LIMIT = 300

EMAIL_MANAGER = "receiverstage@gmail.com"
EMAIL_SENDER = "senderstage@gmail.com"
PASSWORD_EMAIL = "termoregolazione"






@app.route('/values')
def values():
    if not checkToken(request):
        return "401 - Non autorizzato", 401
    raspberry = json.loads(request.data)["raspberry"]
    data = json.loads(request.data)["data"]
    dbUtils.updateLastActivityRaspberry(raspberry)
    for sensor in data:
        sensorType = dbUtils.getSensorType(int(sensor))
        if sensorType == 1:
            window(int(sensor), data[sensor])
        elif sensorType == 2:
            temperature(int(sensor), data[sensor])
        elif sensorType == 3:
            pir(int(sensor), data[sensor])
        elif sensorType == 4:
            button(int(sensor), data[sensor])
        elif sensorType == -2:
            return "No sensor with ID " + str(sensor), 400
        else:
            return "Problem with db", 500
    return "", 200



#il raspberry comunica l'azione avvenuta con successo
@app.route("/done")
def done():
    if not checkToken(request):
        return "401 - Non autorizzato", 401
    data = json.loads(request.data)
    dbUtils.updateLastActivityRaspberry(data["raspberry"])
    if not dbUtils.actionAlreadyDone(data["action"]):
        result = dbUtils.actionDone(data["action"], data["raspberry"])
        if result == -1:
            return "Error with db", 500
        else:
            return "", 200
    else:
        return "", 200



#il raspberry comunica l'azione che non è stato possibile effettuare
@app.route("/notDone")
def notDone():
    if not checkToken(request):
        return "401 - Non autorizzato", 401
    data = json.loads(request.data)
    sensorValue = dbUtils.getActionSensorValueByID(data["action"])
    dbUtils.updateLastActivityRaspberry(data["raspberry"])
    if isinstance(sensorValue, int):
        return "Error in the request"
    else:
        dbUtils.updateLastActivityRaspberry(data["raspberry"])
        sensorValue = dbUtils.getActionSensorValueByID(data["action"])
        msg = "Raspberry " + str(data["raspberry"]) + " ha un problema a settare a " + str(sensorValue[1]) + " il sensore " + str(sensorValue[0])
        newIssue(message=msg, raspberry=data["raspberry"], sensor=sensorValue[0], value=sensorValue[1])
        return "", 200



#viene notificata la risoluzione dell'issue
@app.route("/solved", methods=['GET', 'POST'])
def solved():
    try:
        #ottengo l'issueID dal BarerToken
        token = request.form["token"]
        issueID = jwt.decode(token, key=TOKEN_PASSWORD_EMAIL, algorithms=ALGORITHM)["issueID"]

        #provo a impostare l'issue su risolta e genero la risposta nei vari casi
        result = dbUtils.setIssueSolved(issueID)
        if result == 0:
            return "200 - Issue risolta", 200
        elif result == -1:
            return "404 - L'issue non esiste", 404
        elif result == -2:
            return "200 - L'issue risulta già risolta", 200
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return "401 - Non autorizzato", 401
    except BadRequestKeyError:
        return  "400 - Errore nella richiesta"
    return "", 500



@app.route("/test")
def test():

    return "", 200




##### FUNCTIONS #####

#controlla il token se è corretto
def checkToken(req):
    try:
        auth_header = req.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        jwt.decode(token, key=TOKEN_PASSWORD_API_MANAGEMENT, algorithms=ALGORITHM)
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return False
    return True



#aggiunge una issue e invia una mail all'indirizzo del manager con il testo passato
#-1 se esisteva già quell'issue non risolta
#altrimenti restituisce l'ID dell'issue
def newIssue(message: str, raspberry: int = None, sensor: int = None, value: int = None):
    issueID = dbUtils.addIssue(raspberry, sensor, value)
    if issueID == -2:
        #esisteva già quell'issue non risolta
        return -1
    else:
        #ho appena creato l'issue, genero il codice jwt relativo all'issue
        validation = jwt.encode({"issueID": issueID}, TOKEN_PASSWORD_EMAIL, algorithm=ALGORITHM).decode('utf-8')
        #mando la mail
        subject = "Issue n." + str(issueID)
        msgHtml = """
        <html lang="html">
            <head></head>
            <body>
                <h3>""" + str(message) + """</h3>
                <form action='"""+ HOST + """solved' method="POST">
                    <input type="hidden" name="token" value = '""" + str(validation) + """' />
                    <input type="submit" value="Risolto" />
                </form>
            </body>
        </html>
        """
        sendMailThread(subject, html=msgHtml)
        return issueID



#avvia il thread per mandare la mail, per evitare tempi di attesa
def sendMailThread(subject: str, text: str = None, html: str = None):
    Thread(target=sendMail, args=(subject, text, html)).start()
    return



#funzione per inviare una mail
def sendMail(subject: str, text: str = None, html: str = None):
    s = smtplib.SMTP(host="smtp.gmail.com", port=587)
    s.ehlo()
    s.starttls()
    s.login(EMAIL_SENDER, PASSWORD_EMAIL)

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_MANAGER
    msg['Subject'] = subject
    if text is not None:
        msg.attach(MIMEText(text, 'plain'))
    if html is not None:
        msg.attach(MIMEText(html, "html"))

    s.send_message(msg)
    return




##### SENSORS FUNCTIONS #####

def window(sensorID: int, data):
    print("Data of window " + str(sensorID) + ": " + str(data))
    windowStatus: int
    if isinstance(data, int):
        windowStatus = data
    else:
        windowStatus = data[-1]

    dbUtils.setSensorValue(sensorID, windowStatus)
    ruleUtils.check(sensorID)
    return 200



def temperature(sensorID: int, data):
    print("Data of thermometer " + str(sensorID) + ": " + str(data))
    temp: float
    if isinstance(data, Union[float, int]):
        #viene passato un solo dato
        temp = data
    else:
        #vengono passati più dati
        temp = data[-1]

    dbUtils.setSensorValue(sensorID, temp)
    ruleUtils.check(sensorID)
    return "", 500



def pir(sensorID: int, data):
    print(str(sensorID) + ": " + str(data))
    now = datetime.now()
    strNow = str(now.year) + str(now.month) + str(now.day) + str(now.hour) + str(now.minute) + str(now.second)
    now = int(strNow)

    dbUtils.setSensorValue(sensorID, now)
    ruleUtils.check(sensorID)
    return "", 500



def button(sensorID: int, data):
    print(str(sensorID) + ": " + str(data))
    dbUtils.setSensorValue(sensorID, 1)
    ruleUtils.check(sensorID)
    return "", 500



#threak che controlla periodicamente le assenze negli uffici
def threadPresence():
    while not terminate:
        print("check presence")
        pirs = dbUtils.getPirs()
        for pirSensor in pirs:
            ruleUtils.check(pirSensor)
        time.sleep(SECONDS_BETWEEN_PRESENCE_CHECK)



#thread che controlla l'inattività dei raspberry
def threadInactivity():
    while not terminate:
        print("check inactivity")
        InactiveRaspberrys = dbUtils.getRaspberrysWithInactivity(INACTIVITY_SECONDS_LIMIT)
        for raspberry in InactiveRaspberrys:
            lastActivity = dbUtils.getLastActivityRaspberry(raspberry)
            msg = "Il raspberry " + str(raspberry) + " è inattivo da " + str(lastActivity)
            newIssue(message=msg, raspberry=raspberry, sensor=None, value=None)
        time.sleep(SECONDS_BETWEEN_INACTIVITY_CHECK)










if __name__ == "__main__":
    app.run(host='http://127.0.0.1')

terminate = False

PresenceThread = Thread(target=threadPresence)
PresenceThread.setName("PresenceThread")
PresenceThread.deamon = True

InactivityThread = Thread(target=threadInactivity)
InactivityThread.setName("InactivityThread")
InactivityThread.deamon = True

try:
    PresenceThread.start()
    InactivityThread.start()
except KeyboardInterrupt:
    print("CTRL + C")
    terminate = True
    InactivityThread.join()
    PresenceThread.join()
    exit()