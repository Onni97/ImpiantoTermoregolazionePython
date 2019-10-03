import json, dbUtilsTrentinoDigitale
from flask import Flask, request

app = Flask(__name__)

PALACE = 1






@app.route('/values')
def values():
    data = json.loads(request.data)["data"]
    for sensor in data:
        sensorType = dbUtilsTrentinoDigitale.getSensorType(sensor)
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
    return "", 500



#il raspberry comunica l'azione che non è stato possibile effettuare






##### FINESTRE #####

def window(sensorID: int, data):
    if isinstance(data, int):
        # viene passato solo un dato
        print("Data of window " + str(sensorID) + ": " + str(data))
        if data == 1:
            #la finestra è aperta
            windowOpen(sensorID)
        else:
            #la finestra è chiusa
            windowClosed(sensorID)
        return "", 200
    else:
        # vengon passati piu dati
        print("Data of window " + str(sensorID) + ": " + str(data))
        if data[len(data) - 1]:
            #la finestra è aperta
            windowOpen(sensorID)
        else:
            #la finestra è chiusa
            windowClosed(sensorID)
        return "", 200



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
    print(str(sensorID) + ": " + str(data))
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