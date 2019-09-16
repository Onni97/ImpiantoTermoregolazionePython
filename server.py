import utils

HOST = "localhost"
DATABASE = "dbtermoregolazione"
USERNAME = "root"
PASSWORD = ""

if(utils.checkIfWindowIsOpen(357)):
    print("❌ FINESTRA APERTA")
else:
    print("✔ FINESTRA CHIUSA")
