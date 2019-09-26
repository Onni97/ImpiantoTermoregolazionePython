import jwt, json, threading, requests, mysql
from mysql.connector import Error, cursor
from flask import Flask, request

app = Flask(__name__)

TOKEN_KEY = "termoregolazione"
ALGORITHM = "HS256"

HOST = "localhost"
DATABASE = "todo"
USERNAME = "root"
PASSWORD = ""

#dizionario che associa edificio al gestore
PALACE_SERVICE = {
    1: "http://127.0.0.1:5001/values"
}






##### FUNCTIONS #####

#restituisco l'edificio e il raspberry dalla request
def getPalaceAndRaspberry(req: request) -> (str, str):
    try:
        auth_header = req.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '')
        decoded = jwt.decode(token, key=TOKEN_KEY, algorithms=ALGORITHM)
        return decoded["palace"], decoded["raspberry"]
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return -1, -1



#funzione del thread che si occupa di inviare i valori al gestore delle regole di palazzo
def launchRequest(palace: int, raspberry:int, passedData: dict):
    host = PALACE_SERVICE[palace]
    data = {"raspberry": raspberry,
            "data": passedData}
    requests.get(url=host, json=data)
    return



#restituisce le azioni da fare per un determinato raspberry
def actionsForRaspberry(palace: int, raspberry: int):
    try:
        connection = mysql.connector.connect(host=HOST, database=DATABASE, username=USERNAME, password=PASSWORD)
        if connection.is_connected():
            #ottengo i risultati
            cur = connection.cursor()
            cur.execute("select ID, sensor, value from actionstodo  where palace = " + str(palace) + " and raspberry = " + str(raspberry))
            results = cur.fetchall()

            #li metto nel dizionario e li elimino dal db
            toRtn: dict = {}
            for row in results:
                toRtn[row[1]] = row[2]
                cur.execute("delete from actionstodo where ID = " + str(row[0]))
                connection.commit()

            print(toRtn)
            cur.close()
            connection.close()
            return toRtn
    except Error:
        return  -1






##### APIS #####

#api chiamata dai raspberry per mandare i dati
@app.route("/values")
def values():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:
        threading.Thread(target=launchRequest, args=(palace, raspberry, json.loads(request.data))).start()
        return "", 200



#api chiamata dai raspberry per chiedere le azioni da fare
@app.route("/ping")
def ping():
    palace, raspberry = getPalaceAndRaspberry(request)
    if palace == -1:
        return "", 401
    else:
        results = actionsForRaspberry(palace, raspberry)
        if results == -1:
            return "", 500
        else:
            return "", 200



@app.route("/done")
def actionDone():
    return "", 500






if __name__ == "__main__":
    app.run(host='http://127.0.0.1')