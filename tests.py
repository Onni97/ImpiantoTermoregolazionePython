import utils

HOST = "localhost"
DATABASE = "dbtermoregolazione"
USERNAME = "root"
PASSWORD = ""


#test checkIfWindowIsOpen OK
if utils.checkIfWindowIsOpen(357):
    print("✔ FINESTRA 357 APERTA")
else:
    print("❌ FINESTRA 357 CHIUSA")


#test checkIfOfficeHasOpenedWindows OK
if utils.checkIfOfficeHasOpenedWindows(609):
    print("✔ UFFICIO 609 HA ALMENO UNA FINESTRA APERTA")
else:
    print("❌ UFFICIO 609 HA TUTTE LE FINESTRE CHIUSE")


#test checkIfConditionerIsOn OK
if utils.checkIfConditionerIsOn(823):
    print("✔ CONDIZINOATORE 823 ACCESO")
else:
    print("❌ CONDIZIONATORE 823 SPENTO")


#test checkIfOfficeHasConditionersOn OK
if utils.checkIfOfficeHasConditionersOn(609):
    print("✔ UFFICIO 609 HA ALMENO UN CONDIZINOATORE ACCESO")
else:
    print("❌ UFFICIO 609 HA TUTTI I CONDIZIONATORI SPENTI")


#test lastPresenceInOffice OK
print("🕐 ULTIMA PRESENZA NELL'UFFICIO 609: " + str(utils.lastPresenceInOffice(609)))


#test temperatureInOffice OK
print("🔥 TEMPERATURA NELL'UFFICIO 609: " + str(utils.temperatureInOffice(609)) + "°")


#test
print("🔥 TEMPERATURA PREFERITA NELL'UFFICIO 609: " + str(utils.preferredTemperatureInOffice(609)) + "°")