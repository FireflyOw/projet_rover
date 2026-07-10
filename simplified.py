import sys, os, time, threading
from mouvements import goForward, initServos, scan
from mesures import mesures, ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")

# Initialisation du rover:
rover.init(0)
print("[main.py] rover initialisé!")

# Paramètres rover:
avancer = False
speed = 70
posX = 0
posY = 0

# Paramètres capteurs:
adresse = 0x50
capteur = None

# Paramètres mesure:
lastMesure = 0
intervalMesure = 3
distance = []

# ---- Boucle principale : ----
initServos(rover)

try:
    while True:
        distance.append(rover.getDistance())
        valeurs = mesures(adresse, capteur, rover.bus)

        if avancer == False:
            goForward(rover, speed)
            avancer = True

        if distance[-1] <= 35:
            rover.stop()
            avancer = False

        time.sleep(0.05)

finally:
    rover.cleanup()