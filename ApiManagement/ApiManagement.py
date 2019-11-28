import jwt, json, requests, mysql, time
from mysql.connector import Error
from threading import Thread, Lock
from flask import Flask, request

app = Flask(__name__)

TOKEN_PASSWORD = "termoregolazione"
ALGORITHM = "HS256"

HOST = "localhost"
DATABASE = "todo"
USERNAME = "root"
PASSWORD = ""

TIME_TO_WAIT_FOR_OTHER_EQUALS_REQUESTS = 0.5

#dizionario che associa edificio al gestore
PALACES = {
    1: {
        "host": "http://127.0.0.1:5001/",
        "password": "trentinodigitale"
    }
}

mutexCalls = Lock()
mutexDone = Lock()
sensorsInUse = []






##### FUNCTIONS #####

#restituisco l'edificio e il raspberry dalla request
def getPalaceAndRaspberry(req: request) -> (str, str):
    try:
        auth_header = req.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        decoded = jwt.decode(token, key=TOKEN_PASSWORD, algorithms=ALGORITHM)
        return decoded["palace"], decoded["raspberry"]
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return -1, -1



#funzione del thread che si occupa di inviare i valori al gestore delle regole di palazzo
#restituisce -1 se il sensore è già in uso, altrimenti restituisce la risposta della chiamata
def launchValues(palace: int, raspberry:int, passedData: dict):
    #ottengo il sensore
    sensor = -1
    for k in passedData.keys():
        sensor = k
    if sensor == -1:
        return -1
    else:
        mutexCalls.acquire()
        if (palace, sensor) in sensorsInUse:
            #c'è già una chiamata per quel sensore, esco
            mutexCalls.release()
            return -1
        else:
            #non c'è una chiamata per quel sensore, prendo il "posto"
            sensorsInUse.append((palace, sensor))
            mutexCalls.release()

            #faccio la richiesta
            host = PALACES[palace]["host"] + "values"
            data = {"raspberry": raspberry,
                    "data": passedData}
            token = jwt.encode(payload={}, key=PALACES[palace]["password"], algorithm=ALGORITHM).decode('utf-8')
            header = {'Authorization': 'Bearer ' + token}
            toRtn = requests.get(url=host, json=data, headers=header)

            #aspetto un attimo per bloccare eventuali altri thread che voglion dire la mia stessa cosa
            time.sleep(TIME_TO_WAIT_FOR_OTHER_EQUALS_REQUESTS)
            #rilascio il posto4
            mutexCalls.acquire()
            sensorsInUse.remove((palace, sensor))
            mutexCalls.release()
        return toRtn



#restituisce le azioni da fare per un determinato raspberry
def actionsForRaspberry(palace: int, raspberry: int):
    try:
        connection = mysql.connector.connect(host=HOST, database=DATABASE, username=USERNAME, password=PASSWORD)
        if connection.is_connected():
            #ottengo i risultati
            cur = connection.cursor()
            cur.execute("select a.ID, sensor, value "
                        "from (select * from actionstodo where doneBy is null) a, executors e " +
                        "where a.ID = e.IDAction and a.palace = " + str(palace) + " and IDExecutor = " + str(raspberry))
            results = cur.fetchall()

            #li metto nel dizionario
            toRtn: dict = {}
            cnt = 0
            for row in results:
                toRtn[cnt] = {"actionID": row[0], "sensor": row[1], "value": row[2]}
                cnt = cnt + 1

            if toRtn == {}:
                return -2
            cur.close()
            connection.close()
            return toRtn
        else:
            return -1
    except Error:
        return -1



#effettuo la chiamata di un'azione avvenuta con successo
def launchDone(palace: int, raspberry:int, actionDone: int):
    host = PALACES[palace]["host"] + "done"
    data = {"raspberry": raspberry,
            "action": actionDone}
    token = jwt.encode(payload={}, key=PALACES[palace]["password"], algorithm=ALGORITHM).decode('utf-8')
    header = {'Authorization': 'Bearer ' + token}
    requests.get(url=host, json=data, headers=header)
    return



#effettuo la chiamata di un'azione non avvenuta con successo
def launchNotDone(palace: int, raspberry: int, actionNotDone: int):
    host = PALACES[palace]["host"] + "notDone"
    data = {"raspberry": raspberry,
            "action": actionNotDone}
    token = jwt.encode(payload={}, key=PALACES[palace]["password"], algorithm=ALGORITHM).decode('utf-8')
    header = {'Authorization': 'Bearer ' + token}
    requests.get(url=host, json=data, headers=header)
    return






##### APIS #####

#api chiamata dai raspberry per mandare i dati
@app.route("/values")
def values():
    try:
        palace, raspberry = getPalaceAndRaspberry(request)
        data = json.loads(request.data)
        if palace == -1:
            return "", 401
        else:
            for sensorData in data:
                Thread(target=launchValues, args=(palace, raspberry, {sensorData: data[sensorData]})).start()
            return "", 200
    except json.decoder.JSONDecodeError:
        return "Error with the passed data", 500



#api per azioni prioritarie, non usa i thread
@app.route("/priority")
def priority():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:

        response = launchValues(palace, raspberry, json.loads(request.data))
        if response == 200:
            result = actionsForRaspberry(palace, raspberry)
            if result == -1:
                #Errore
                return "Error with dbTodo", 500
            elif result == -2:
                #non ci sono anzioni da fare
                return "No action needed", 200
            else:
                return result, 200

        elif response == 400:
            return "No sensor with ID " + str(request.data[0]), 400
        elif response == 500:
            return "Error with dbTrentinoDigitale"



#api chiamata dai raspberry per chiedere le azioni da fare
@app.route("/ping")
def ping():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:
        result = actionsForRaspberry(palace, raspberry)
        if result == -1:
            return "", 500
        elif result == -2:
            # non ci sono anzioni da fare
            return "No action needed", 200
        else:
            return result, 200



#api per comunicare che l'azione è stata eseguita
@app.route("/done")
def done():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:
        if isinstance(json.loads(request.data), int):
            Thread(target=launchDone, args=(palace, raspberry, json.loads(request.data))).start()
            return "", 200
        else:
            return "", 400



#api per comunicare che c'è stato un problema nell'eseguire l'azione
@app.route("/notDone")
def NotDone():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:
        if isinstance(json.loads(request.data), int):
            Thread(target=launchNotDone, args=(palace, raspberry, json.loads(request.data))).start()
            return "", 200
        else:
            return "", 400






if __name__ == "__main__":
    app.run(host='http://127.0.0.1')