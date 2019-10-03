from typing import Optional, Dict, List, Any, Union

import mysql.connector
from mysql.connector import Error, cursor

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
    __host: str = None
    __database: str = None
    __username: str = None
    __password: str = None
    __connection: mysql.connector.connection = None
    __cursor: mysql.connector.cursor = None

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
            self.__connection.close()
            return
        except Error as e:
            return

    def query(self, query: str) -> cursor:
        try:
            self.__connection = mysql.connector.connect(host=self.__host,
                                                        database=self.__database,
                                                        username=self.__username,
                                                        password=self.__password)
            if self.__connection.is_connected():
                self.__cursor = self.__connection.cursor()
                self.__cursor.execute(query)
                return self.__cursor.fetchall()
            else:
                return -1
        except Error as e:
            return -1

    def execute(self, query: str):
        try:
            self.__connection = mysql.connector.connect(host=self.__host,
                                                        database=self.__database,
                                                        username=self.__username,
                                                        password=self.__password)
            if self.__connection.is_connected():
                self.__cursor = self.__connection.cursor()
                self.__cursor.execute(query)
                self.__connection.commit()
            else:
                return -1
        except Error as e:
            return -1


    def closeCursor(self):
        if self.__connection.is_connected() and self.__cursor is not None:
            self.__cursor.close()
            self.__cursor = None
            return
        else:
            return -1

    def closeConnection(self):
        if self.__connection.is_connected():
            self.__connection.close()
            return
        else:
            return -1
#########################



#restituisce il tipo del sensore passato, -1 se c'è un problema con il db o -2 se non c'è un'entry nel db con quel sensorID
def getSensorType(sensorID: int) -> int:
    database = db(HOST, DATABASE, USERNAME, PASSWORD)
    result: Union[None, list] = database.query("select type from sensors where ID = " + str(sensorID))
    toRtn: int
    if result == -1 or result is None:
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

    return



#restituisce gli ID dei raspberry collegati ad un sensore
def getRaspberryForSensor(sensorID):
    return



#elimina l'azione dal dbTodo e restituisce sensor e value dell'azione appena eliminata
def deleteAction(actionID):
    return