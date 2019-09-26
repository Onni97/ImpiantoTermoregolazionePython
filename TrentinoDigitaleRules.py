import jwt, json, dbUtilsTrentinoDigitale
from flask import Flask, request

app = Flask(__name__)

PALACE = 1






@app.route('/values')
def values():
    data = json.loads(request.data)["data"]
    for sensor in data:
        sensorType = dbUtilsTrentinoDigitale.getSensorType(sensor)
        if sensorType == 1:
            #window
            window(sensor, data[sensor])




    return "", 200






##### FINESTRE #####

def window(sensor: int, data):
    return 0



def finestraAperta(idWindow, data):
    if isinstance(data, int):
        # viene passato solo un dato
        return 500
    else:
        # vengon passati piu dati
        return 500




def finestraChiusa(IDWindow=None):
    return 500




def temperatura(IDOffice=None):
    return 500




def PIRPresente(IDPIR=None):
    return 500




def PIRAssente(IDPIR=None):
    return 500





if __name__ == "__main__":
    app.run(host='http://127.0.0.1')