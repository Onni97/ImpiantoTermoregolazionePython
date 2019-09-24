import jwt
from flask import Flask, request
app = Flask(__name__)

PALACE = 1


@app.route('/values')
def values():
    return 500



def finestraAperta(IDWindow=None):
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
    app.run(host= '127.0.0.1', port=5001)