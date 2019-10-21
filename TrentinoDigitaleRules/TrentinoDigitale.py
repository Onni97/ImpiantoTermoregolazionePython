import json
from flask import Flask, request
import dbUtils

app = Flask(__name__)

PALACE = 1

#todo: thread che vede l'inattività dei raspberry




@app.route('/values')
def values():
    raspberry = json.loads(request.data)["raspberry"]
    data = json.loads(request.data)["data"]
    dbUtils.updateLastActivityRaspberry(raspberry)
    for sensor in data:
        sensorType = dbUtils.getSensorType(sensor)
        if sensorType == 1:
            window(sensor, data[sensor])
        elif sensorType == 2:
            temperature(sensor, data[sensor])
        elif sensorType == 3:
            pir(sensor, data[sensor])
        elif sensorType == 4:
            conditioneer(sensor, data[sensor])
        elif sensorType == 5:
            button(sensor, data[sensor])
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
    if not dbUtils.actionAlreadyDone(data["action"], data["raspberry"]):
        result = dbUtils.actionDone(data["action"], data["raspberry"])
        if result == -1:
            return "", 500
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





##### FINESTRE #####

def window(sensorID: int, data):
    print("Data of window " + str(sensorID) + ": " + str(data))
    windowStatus: int
    if isinstance(data, int):
        windowStatus = data
    else:
        windowStatus = data[len(data) - 1]

    if windowStatus:
        windowOpen(sensorID)
    else:
        windowClosed(sensorID)

    return 200



#la finestra viene cihusa
def windowClosed(sensorID: int):
    print("    Aggiorno il db, la finestra " + str(sensorID) + " è chiusa")
    return



#la finestra viene aperta
def windowOpen(sensorID: int):
    print("    Aggiorno il db, la finestra " + str(sensorID) + " è aperta")
    return






##### TEMPERATURA #####

def temperature(sensorID: int, data):
    print("Data of thermometer " + str(sensorID) + ": " + str(data))
    if isinstance(data, int):
        #viene passato un solo dato
        print()
    else:
        #vengono passati più dati
        print()
    return "", 500






##### PIR #####

def pir(sensorID: int, data):
    print(str(sensorID) + ": " + str(data))
    return "", 500






##### CONDIZIONATORI #####

def conditioneer(sensorID: int, data):
    print(str(sensorID) + ": " + str(data))
    return "", 500






##### BUTTON #####

def button(sensorID: int, data):
    print(str(sensorID) + ": " + str(data))
    return "", 500






if __name__ == "__main__":
    app.run(host='http://127.0.0.1')




#todo: si potrebbe fare un thread che controlla i raspberry inattivi da tempo, in caso manda un avviso per email