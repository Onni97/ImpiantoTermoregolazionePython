import mysql.connector
import datetime
from mysql.connector import Error, cursor

HOST = "localhost"
DATABASE = "dbtermoregolazione"
USERNAME = "root"
PASSWORD = ""

##### DB CONNECTOR #####
class db(object):
    __database: str = None
    __username: str = None
    __password: str = None
    __connection: mysql.connector.connection = None
    __cursor: mysql.connector.cursor = None

    def __init__(self, host: str, database: str, username: str, password: str):
        try:
            self.__database = database
            self.__username = username
            self.__password = password
            self.__connection = mysql.connector.connect(host=host,
                                                        database=database,
                                                        user=username,
                                                        password=password)
            self.__cursor = None
            return
        except Error as e:
            print("Error reading data from MySQL table", e)

    def query(self, query: str) -> cursor:
        if self.__connection.is_connected():
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute(query)
            return self.__cursor.fetchall()
        else:
            return -1

    def closeCursor(self):
        if self.__connection.is_connected() and self.__cursor is not None:
            self.__cursor.close;
            self.__cursor = None
            return
        else:
            return -1

    def closeConnection(self):
        if self.__connection.is_connected():
            self.__connection.close
            return
        else:
            return -1
##########




#controlla se la finestra passata è aperta
def checkIfWindowIsOpen(IDWindow: int) -> bool:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select isOpen from finestre where ID = " + str(IDWindow))
    isOpen = result[0][0]

    database.closeCursor()
    database.closeConnection()
    if isOpen:
        return True
    else:
        return False



#controlla se l'ufficio passato ha almeno una finestra aperta
def checkIfOfficeHasOpenedWindows(IDOffice: int) -> bool:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select isOpen from finestre where IDUfficio = " + str(IDOffice))

    hasOpenedWindows = False
    for window in result:
        hasOpenedWindows = hasOpenedWindows or window[0]

    database.closeCursor()
    database.closeConnection()
    return hasOpenedWindows



#controlla se il condizionatore passato è acceso
def checkIfConditionerIsOn(IDConditioner: int) -> bool:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select isOn from tagliacorrente where ID = " + str(IDConditioner))
    isOn = result[0][0]

    database.closeCursor()
    database.closeConnection()
    return isOn



#controlla se un ufficio ha condizionatori accesi
def checkIfOfficeHasConditionersOn(IDOffice: int) -> bool:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select isOn from tagliacorrente where IDUfficio = " + str(IDOffice))

    hasConditionersOn = False
    for conditioner in result:
        hasConditionersOn = hasConditionersOn or conditioner[0]

    database.closeCursor()
    database.closeConnection()
    return hasConditionersOn



#restituisce l'ora dell'ultima presenza nell'ufficio passato
def lastPresenceInOffice(IDOffice: int) -> datetime.timedelta:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select max(lastPresenceTime) " +
                            "from sensoridimovimento " +
                            "where IDUfficio = " + str(IDOffice) + " " +
                            "group by IDUfficio")
    lastPresence = result[0][0]

    database.closeCursor()
    database.closeConnection()
    return lastPresence



#restituisce la temperatura in un ufficio
def temperatureInOffice(IDOffice: int):
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select ultimaTemperatura from uffici where ID = " + str(IDOffice))
    temperature = result[0][0]

    database.closeCursor()
    database.closeConnection()
    return temperature
