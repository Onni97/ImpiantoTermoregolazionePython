import mysql.connector
from mysql.connector import Error, cursor
from datetime import datetime
from typing import Union
import pymysql.cursors

PALACE_ID = 1

#per i sensori
HOST = "localhost"
DATABASE = "dbtrentinodigitalev2"
USERNAME = "root"
PASSWORD = ""

#per le azioni da attuare
HOST_TODO = "localhost"
DATABASE_TODO = "todo"
USERNAME_TODO = "root"
PASSWORD_TODO = ""




##### DB CONNECTOR #####
class db(object):

    def __init__(self, host: str, database: str, username: str, password: str):
        try:
            self.__host = host
            self.__database = database
            self.__username = username
            self.__password = password
            self.__connection = mysql.connector.connect(host=self.__host,
                                                        database=self.__database,
                                                        username=self.__username,
                                                        password=self.__password)
            self.__cursor = self.__connection.cursor()
            return
        except Error:
            print("Error connecting the database")
            return

    def query(self, query: str) -> mysql.connector.cursor:
        if self.__connection.is_connected():
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute(query)
            self.__connection.commit()
            return self.__cursor.fetchall()

    def execute(self, query: str):
        if self.__connection.is_connected():
            self.__cursor = self.__connection.cursor()
            self.__cursor = self.__connection.cursor()
            self.__cursor.execute(query)
            self.__connection.commit()
            return 0


    def closeCursor(self):
        self.__cursor.close()
        return 0

    def closeConnection(self):
        if self.__connection.is_connected():
            self.__connection.close()
            return 0
        else:
            return -1
#########################



#restituisce il tipo del sensore passato, -1 se c'è un problema con il db o -2 se non c'è un'entry nel db con quel sensorID
def getSensorType(sensorID: int) -> int:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select type from sensors where ID = %s" % str(sensorID))
    toRtn: int
    if result == -1:
        toRtn = -1
    else:
        if len(result) == 0:
            toRtn = -2
        else:
            toRtn = result[0][0]
    database.closeCursor()
    database.closeConnection()
    return toRtn



#imposta il valore di un sensore
def setSensorValue(sensorID: int, value: int):
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.execute("update sensors set value = " + str(value) + " where ID = " + str(sensorID))
    database.closeCursor()
    database.closeConnection()
    if result == -1:
        return -1
    else:
        return 0



#restituisce gli ID dei raspberry collegati ad un sensore
def getRaspberrysForSensor(sensorID):
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result = database.query("select r.ID "
                            "from raspberry r, sensors s, raspberry_sensor rs " +
                            "where r.ID = rs.IDRaspberry and s.ID = rs.IDSensor and s.ID = " + str(sensorID) + " "
                            "order by r.lastActivity desc")
    toRtn: Union[int, list]
    if result == -1:
        toRtn = -1
    else:
        if len(result) == 0:
            toRtn = -2
        else:
            toRtn = []
            for row in result:
                toRtn.append(row[0])
    database.closeCursor()
    database.closeConnection()
    return toRtn



#aggiunge un'azione da compiere nel dbTodo
def addAction(raspberrys: Union[list, int], sensor: int, value: int):
    now = datetime.now()
    connection = pymysql.connect(host=HOST_TODO,
                               user=USERNAME_TODO,
                               password=PASSWORD_TODO,
                               db=DATABASE_TODO)
    try:
        #inserisco l'azione
        with connection.cursor() as cur:
            query = "insert into actionstodo(palace, sensor, value, dateTimeInsert) " \
                    "values(%s, %s, %s, '%s')" \
                    % (str(PALACE_ID), str(sensor), str(value), datetime.strftime(now, "%Y-%m-%d %H:%M:%S"))
            cur.execute(query)
        connection.commit()

        #ottengo l'ID dell'azione appena inserita
        with connection.cursor() as cur:
            query = "select ID " \
                    "from actionstodo " \
                    "where palace = %s and sensor = %s and dateTimeInsert = '%s'" \
                    % (str(PALACE_ID), str(sensor), datetime.strftime(now, "%Y-%m-%d %H:%M:%S"))
            cur.execute(query)
            result = cur.fetchall()
            idAction = result[0][0]

        #inserisco tutti gli esecutori per quell'azione
        query = "insert into executors(IDAction, IDExecutor) values "
        for raspberry in raspberrys:
            query += " (%s, %s)," % (str(idAction), str(raspberry))
        query = query[:-1]
        with connection.cursor() as cur:
            cur.execute(query)
        connection.commit()

    finally:
        connection.close()
        return 0



#elimina l'azione dal dbTodo e restituisce sensor e value dell'azione appena eliminata
def actionDone(actionID: int, raspberry: int):
    now = datetime.now()
    connection = pymysql.connect(host=HOST_TODO,
                                 user=USERNAME_TODO,
                                 password=PASSWORD_TODO,
                                 db=DATABASE_TODO)
    try:
        #aggiorno l'actiondone
        with connection.cursor() as cur:
            query = "update actionstodo " \
                    "set doneBy = %s and dateTimeDone = %s " \
                    "where palace = %s and ID = %s" \
                    % (str(raspberry), datetime.strftime(now, "%Y-%m-%d %H:%M:%S"), str(PALACE_ID), str(actionID))
            cur.execute(query)
        connection.commit()

        #aggiorno illastActivity del raspberry
        updateLastActivityRaspberry(raspberry)

    finally:
        connection.close()
        return 0



#restituisce true se l'azione è già stata effettuata
def actionAlreadyDone(actionID: int, raspberry: int):
    toRtn = False
    connection = pymysql.connect(host=HOST_TODO,
                                 user=USERNAME_TODO,
                                 password=PASSWORD_TODO,
                                 db=DATABASE_TODO)
    try:
        #controllo se l'azione è già stata fatta
        with connection.cursor() as cur:
            query = "select doneBy from actionstodo where ID = %s" % (str(actionID))
            cur.execute(query)
            result = cur.fetchall()
            if result[0][0] is not None:
                toRtn = True

        # aggiorno illastActivity del raspberry
        updateLastActivityRaspberry(raspberry)

    finally:
        connection.close()
    return toRtn



#aggiorna la lastActivity del raspberry passato con l'ora attuale
def updateLastActivityRaspberry(raspberry: int):
    now = datetime.now()
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "update raspberry " \
                    "set lastActivity = '%s' " \
                    "where ID = %s" \
                    % (datetime.strftime(now, "%Y-%m-%d %H:%M:%S"), str(raspberry))
            cur.execute(query)
        connection.commit()
    finally:
        connection.close()
        return 0