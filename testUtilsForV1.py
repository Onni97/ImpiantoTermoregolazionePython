import dbUtilsForV1
import time

HOST = "localhost"
DATABASE = "dbtermoregolazione"
USERNAME = "root"
PASSWORD = ""



#test checkIfWindowIsOpen OK
if dbUtilsForV1.checkIfWindowIsOpen(357):
    print("✔ FINESTRA 357 APERTA")
else:
    print("❌ FINESTRA 357 CHIUSA")


#test checkIfOfficeHasOpenedWindows OK
if dbUtilsForV1.checkIfOfficeHasOpenedWindows(609):
    print("✔ UFFICIO 609 HA ALMENO UNA FINESTRA APERTA")
else:
    print("❌ UFFICIO 609 HA TUTTE LE FINESTRE CHIUSE")


#test checkIfConditionerIsOn OK
if dbUtilsForV1.checkIfConditionerIsOn(823):
    print("✔ CONDIZINOATORE 823 ACCESO")
else:
    print("❌ CONDIZIONATORE 823 SPENTO")


#test checkIfOfficeHasConditionersOn OK
if dbUtilsForV1.checkIfOfficeHasConditionersOn(609):
    print("✔ UFFICIO 609 HA ALMENO UN CONDIZINOATORE ACCESO")
else:
    print("❌ UFFICIO 609 HA TUTTI I CONDIZIONATORI SPENTI")


#test lastPresenceInOffice OK
print("🕐 ULTIMA PRESENZA NELL'UFFICIO 609: " + str(dbUtilsForV1.lastPresenceInOffice(609)))


#test temperatureInOffice OK
print("🔥 TEMPERATURA NELL'UFFICIO 609: " + str(dbUtilsForV1.temperatureInOffice(609)) + "°")


#test
print("🔥 TEMPERATURA PREFERITA NELL'UFFICIO 609: " + str(dbUtilsForV1.preferredTemperatureInOffice(609)) + "°")

#TODO: test setWindowOnOpend and setWindowOnClosed

#TODO: test setConditionerOnOn and setConditionerOnOff

#TODO: test setLastPresenceOfPIR

#TODO: test addPreferredTemperature

#TODO: test setTemperatureInOffice

#TODO: test checkIfOfficeIsManualMode

#TODO: test setManualModeForOffice

#TODO: test setAutomaticModeForOffice