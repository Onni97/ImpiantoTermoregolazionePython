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








#restituisce il tipo del sensore passato, -1 se c'è un problema con il db o -2 se non c'è un'entry nel db con quel sensorID
def getSensorType(sensorID: int):
    sensorType: int
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select type " \
                    "from sensors " \
                    "where ID = %i" \
                    % sensorID
            cur.execute(query)
            result = cur.fetchall()
            sensorType = result[0][0]
        connection.commit()
    finally:
        connection.close()

    return sensorType



#leggo il valore di un sensore
def getSensorValue(sensorID: int):
    value: int
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select value " \
                    " from sensors " \
                    " where ID = " + str(sensorID)
            cur.execute(query)
            result = cur.fetchall()
            value = result[0][0]
        connection.commit()
    finally:
        connection.close()

    return value



#imposta il valore di un sensore
def setSensorValue(sensorID: int, value):
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "update sensors set value = " + str(value) + " where ID = " + str(sensorID)
            cur.execute(query)
        connection.commit()
    finally:
        connection.close()
    return 0



#restituisce gli ID dei raspberry collegati ad un sensore
def getRaspberrysForSensor(sensorID):
    raspberrys = []
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select r.ID " \
                    " from raspberry r, sensors s, raspberry_sensor rs " \
                    " where r.ID = rs.IDRaspberry and s.ID = rs.IDSensor and s.ID = " + str(sensorID) + " " \
                    " order by r.lastActivity desc"
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                raspberrys.append(row[0])
        connection.commit()
    finally:
        connection.close()

    return raspberrys



#restituisce l'azione dall'ID, -1 se non esiste
def getActionSensorValueByID(actionID: int):
    action = -1
    connection = pymysql.connect(host=HOST_TODO,
                               user=USERNAME_TODO,
                               password=PASSWORD_TODO,
                               db=DATABASE_TODO)
    try:
        with connection.cursor() as cur:
            query = "select sensor, value " \
                    "from actionstodo " \
                    "where ID = %i" \
                    % actionID
            cur.execute(query)
            result = cur.fetchall()
            if len(result) == 1:
                action = result[0]
        connection.commit()
    finally:
        connection.close()
    return action




#aggiunge un'azione da compiere nel dbTodo, restituisce -2 se l'azione non avrebbe alcun effetto
def addAction(raspberrys: Union[list, int], sensor: int, value: int):
    now = datetime.now()
    connection = pymysql.connect(host=HOST_TODO,
                               user=USERNAME_TODO,
                               password=PASSWORD_TODO,
                               db=DATABASE_TODO)
    if getSensorValue(sensor) != value:
        try:
            #controllo se c'è già un'azione non svolta uguale a quella che devo inserire
            insert = True
            with connection.cursor() as cur:
                query = "select * " \
                        "from actionstodo " \
                        "where palace = %i and sensor = %i and value = %i and doneBy is null" \
                        % (PALACE_ID, sensor, value)
                cur.execute(query)
                result = cur.fetchall()
                if len(result) != 0:
                    insert = False
            connection.commit()

            if insert:
                #se non c'è inserisco l'azione
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
                connection.commit()

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
    else:
        return -2



#imposta l'azione su done
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
                    "set doneBy = %s, dateTimeDone = '%s' " \
                    "where palace = %s and ID = %s" \
                    % (str(raspberry), datetime.strftime(now, "%Y-%m-%d %H:%M:%S"), str(PALACE_ID), str(actionID))
            cur.execute(query)
        connection.commit()
        #aggiorno il valore del sensore
        with connection.cursor() as cur:
            query = "select sensor, value " \
                    "from actionstodo " \
                    "where ID = %i" % actionID
            cur.execute(query)
            result = cur.fetchall()
            sensor = result[0][0]
            value = result[0][1]
        connection.commit()
        setSensorValue(sensor, value)
    finally:
        connection.close()
        return 0



#restituisce true se l'azione è già stata effettuata
def actionAlreadyDone(actionID: int) -> bool:
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



def checkIfOfficeHasOpenWindows(office: int) -> bool:
    hasOpenWindows = False
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select sensors.value " \
                    "from sensors, offices " \
                    "where sensors.IDOffice = offices.ID and sensors.type = 1 and offices.ID = %s" \
                    % str(office)
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                if row[0]:
                    hasOpenWindows = True
        connection.commit()
    finally:
        connection.close()
    return hasOpenWindows



def getAverageT(office: int):
    averageT: float
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select avg(value) " \
                    "from savedtemperatures " \
                    "where IDOffice = %s " \
                    "group by IDOffice" \
                    % str(office)
            cur.execute(query)
            result = cur.fetchall()
            averageT = result[0][0]
        connection.commit()
    finally:
        connection.close()
    return averageT



#restituisce l'ufficio del sensore, -2 se il sensore non è in un ufficio
def getOfficeBySensor(sensor: int):
    office: int
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select IDOffice " \
                    "from sensors " \
                    "where ID = %s" \
                    % str(sensor)
            cur.execute(query)
            result = cur.fetchall()
            office = result[0][0]
        connection.commit()
    finally:
        connection.close()

    if office is None:
        return -2
    else:
        return office



#restituisce l'ultima presenza nell'ufficio
def getLastPresenceInOffice(office: int):
    lastPresence: float
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select max(value) " \
                    "from sensors " \
                    "where type = 3 and IDOffice = %s " \
                    "group by IDOffice" \
                    % str(office)
            cur.execute(query)
            result = cur.fetchall()
            lastPresence = result[0][0]
        connection.commit()
    finally:
        connection.close()
    return lastPresence



#restituice tutti i pir
def getPirs():
    toRtn = []
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select ID " \
                    "from sensors " \
                    "where type = 3"
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                toRtn.append(row[0])
        connection.commit()
    finally:
        connection.close()
    return toRtn



#restituisce i condizionatori di un ufficio
def getConditioneerOfOffice(office: int):
    toRtn = []
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select ID " \
                    "from sensors " \
                    "where IDOffice = %i and type = 5" \
                    % office
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                toRtn.append(row[0])
        connection.commit()
    finally:
        connection.close()
    return toRtn



#restituisce le regole relative a un certo sensore e ufficio
def getRuleBySensor(sensor: int):
    rules = []
    office = getOfficeBySensor(sensor)
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            if office == -2:
                #il sensore non è in un ufficio
                #per questa implementazione ipotizzo che non ci possano essere sensori senza un ufficio
                print("SENSORE FUORI DA UN UFFICIO - FEATURE COOMING SOON")
                return []
                #query = "select rule, conseguence " \
                #        "from rules " \
                #        "where rule like '%" + str(sensor) + "%'"
            else:
                # il sensore è in un ufficio
                query = "select rule, conseguence " \
                        "from rules " \
                        "where (rule like '%" + str(sensor) + "%') or (rule like '%" + str(office) + "%') or (rule like '%ufficioX%')"
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                rules.append([row[0], row[1]])
        connection.commit()
    finally:
        connection.close()
    return rules



#restituisce tutti gli id dei raspberry
def getRaspberrys():
    raspberrys = []
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select ID " \
                    "from raspberry"
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                raspberrys.append(row[0])
        connection.commit()
    finally:
        connection.close()
    return raspberrys



#restituisce i raspberry inattivi da più del tempo passato (in secondi)
def getRaspberrysWithInactivity(maxAInactivity: int):
    raspberrys = []
    now = datetime.now()
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select ID, lastActivity " \
                    "from raspberry"
            cur.execute(query)
            result = cur.fetchall()
            for row in result:
                inactivity = now - row[1]
                inactivity = inactivity.days * 86400 + inactivity.seconds
                if inactivity > maxAInactivity:
                    raspberrys.append(row[0])
        connection.commit()
    finally:
        connection.close()
    return raspberrys



#restituisce il datetime dell'ultima attività del raspberry passato
#restituisce -1 se non esiste il raspberry passato
def getLastActivityRaspberry(raspberry: int):
    toRtn = -1
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select lastActivity " \
                    "from raspberry " \
                    "where ID = %i" \
                    % raspberry
            cur.execute(query)
            result = cur.fetchall()
            if len(result) == 1:
                toRtn = result[0][0]
    finally:
        connection.close()
    return toRtn



#aggiunge una nuova issua, restituisce -2 se esiste già una issue uguale non ancora risolta, altrimenti restituisce l'ID dell'issue appena aggiunta
def addIssue(raspberry = None, sensor = None, value = None):
    toRtn: int
    if checkIssue(raspberry=raspberry, sensor=sensor, value=value) == -2:
        #controllo se esiste già un'issue uguale non risolta
        connection = pymysql.connect(host=HOST,
                                     user=USERNAME,
                                     password=PASSWORD,
                                     db=DATABASE)
        try:
            #creo la stringa
            now = datetime.now()

            if raspberry is None:
                raspberryString = "null"
            else:
                raspberryString = raspberry

            if sensor is None:
                sensorString = "null"
            else:
                sensorString = sensor

            if value is None:
                valueString = "null"
            else:
                valueString = value

            query = "insert into issues (timeInsert, raspberry, sensor, value) " \
                    "values('%s', %s, %s, %s) " \
                    % (str(now), str(raspberryString), str(sensorString), str(valueString))
            with connection.cursor() as cur:
                cur.execute(query)
            connection.commit()
            issueID = checkIssue(raspberry=raspberry, sensor=sensor, value=value)
            if issueID == -2:
                toRtn = -1
            else:
                toRtn = issueID
        finally:
            connection.close()
    else:
        return -2
    return toRtn



#restituisce l'ID se esiste già un'issue con gli stessi valori e non risolta, -2 altrimenti
def checkIssue(raspberry = None, sensor = None, value = None):
    toRtn: int
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        #creo la query
        if raspberry is None:
            raspberryString = "is null"
        else:
            raspberryString = "= " + str(raspberry)

        if sensor is None:
            sensorString = "is null"
        else:
            sensorString = "= " + str(sensor)

        if value is None:
            valueString = "is null"
        else:
            valueString = "= " + str(value)

        query = "select ID " \
                "from issues " \
                "where raspberry %s and sensor %s and value %s and timeSolved is null" \
                % (raspberryString, sensorString, valueString)

        with connection.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            if len(result) == 0:
                toRtn = -2
            else:
                toRtn = result[0][0]
        connection.commit()
    finally:
        connection.close()
    return toRtn



#imposta l'issue su risolta
#restituisce 0 se va tutto bene, -1 se l'issue non esiste, -2 se è già risolta
def setIssueSolved(IDIssue):
    alreadySolved = isIssueSolved(IDIssue)
    if alreadySolved == -1:
        return -1
    elif alreadySolved == 1:
        return -2
    else:
        connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
        now = datetime.now()
        query = "update issues " \
                "set timeSolved = '%s' " \
                "where ID = %i" \
                % (str(now), IDIssue)
        try:
            with connection.cursor() as cur:
                cur.execute(query)
            connection.commit()
        finally:
            connection.close()
        return 0



#controlla se l'issue è risolta
#resituisce 1 se è risolta, 0 se non è risolta, -1 se l'issue non esiste
def isIssueSolved(IDIssue):
    toRtn: int
    connection = pymysql.connect(host=HOST,
                                 user=USERNAME,
                                 password=PASSWORD,
                                 db=DATABASE)
    try:
        with connection.cursor() as cur:
            query = "select timeSolved " \
                    "from issues " \
                    "where ID = %i" \
                    % IDIssue
            cur.execute(query)
            result = cur.fetchall()
            if len(result) == 0:
                toRtn = -1
            else:
                if result[0][0] is not None:
                    toRtn = 1
                else:
                    toRtn = 0
    finally:
        connection.close()
    return toRtn


