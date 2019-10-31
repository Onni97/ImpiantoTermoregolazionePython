import json
import time
from _ctypes import Union
from datetime import datetime
from threading import Thread
from flask import Flask, request
import dbUtils, ruleUtils

app = Flask(__name__)

PALACE = 1
SECONDS_BETWEEN_PRESENZE_CHECK = 5


#email sender senderstage@gmail.com
#email receiver receiverstage@gmail.com
#password termoregolazione






@app.route('/values')
def values():
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


@app.route("/test")
def test():
    print(dbUtils.addAction([1,2,3], 111, 222))
    return "", 200



#il raspberry comunica l'azione che non è stato possibile effettuare
#todo





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
        pirs = dbUtils.getPirs()
        for pirSensor in pirs:
            ruleUtils.check(pirSensor)
        time.sleep(SECONDS_BETWEEN_PRESENZE_CHECK)



#thread che controlla l'inattività dei raspberry
#todo def threadInactivity():






terminate = False

thread = Thread(target=threadPresence)
thread.setName("ThreadPresence")
thread.deamon = True
thread.do_run = True
try:
    thread.start()
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("CTRL + C")
    terminate= True
    thread.join()
    exit()



if __name__ == "__main__":
    app.run(host='http://127.0.0.1')





#todo: si potrebbe fare un thread che controlla i raspberry inattivi da tempo, in caso manda un avviso per email