import jwt, json, threading, requests
from flask import Flask, request

app = Flask(__name__)

TOKEN_KEY = "termoregolazione"
ALGORITHM = "HS256"

#dizionario che associa edificio al gestore
edificio_Gestore = {
    1: "127.0.0.1:5001"
}

#dalla request restituisce il token
def getToken(req: request) -> str :
    auth_header = req.headers.get('Authorization', '')
    token = auth_header.replace('Bearer ', '')
    return token

#funzione del thread che si occupa di inviare i valori al gestore delle regole di palazzo
def launchRequest(decoded, passedData):
    host = edificio_Gestore[decoded["edificio"]]
    data = {"raspberry": decoded["raspberry"],
            "data": json.loads(passedData)}
    print("to " + host + " with " + str(data))
    #r = requests.get(host, data)
    return





#api chiamata dai raspberry per mandare i dati
@app.route("/values")
def values():
    try:
        token = getToken(request)
        decoded = jwt.decode(token, key=TOKEN_KEY, algorithms=ALGORITHM)

        threading.Thread(target=launchRequest, args=(decoded, request.data)).start()
        return "", 200
    except (jwt.InvalidSignatureError, jwt.DecodeError):
        return "", 401





#api chiamata dai raspberry per chiedere le azioni da fare
@app.route("/ping")
def ping():
    return 500










if __name__ == "__main__":
    app.run(host='http://127.0.0.1', port=5000)