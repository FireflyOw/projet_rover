import sys, os, time, adafruit_dht, board, smbus2, threading
from mouvements import goForward, initServos, scan
from mesures import mesures, ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")

# Paramètres capteurs:
adresse = 0x50
bus = smbus2.SMBus(1)
try:
    capteur = adafruit_dht.DHT22(board.D25)
except AttributeError:
    capteur = None
    print("[main.py][DHT22] Capteur indisponible!")

# Paramètres mesure:
lastMesure = 0
intervalMesure = 3
distance = []

# Paramètres rover:
avancer = False
speed = 70
posX = 0
posY = 0

# ---- Boucle principale : ----
rover.init(0)
initServos(rover)
print("[main.py] rover initialisé!")

while True:
    try:
        distance.append(rover.getDistance())

        if avancer == False:
            goForward(rover, speed)
            avancer = True

        if time.time() >= lastMesure + intervalMesure:
            valeurs = mesures(adresse, capteur, bus)
            ecriture(adresse, capteur, bus, posX, posY)

            print(f"""
--- Mesures: ---                  
Temp: {valeurs['temperature']} {valeurs['unite_temp']} | Hum: {valeurs['humidite']} {valeurs['unite_hum']}
Distance: {int(distance[-1])}cm
            """)
            lastMesure = time.time()

        if distance[-1] <= 35:
            rover.stop()
            avancer = False

        time.sleep(0.05)

    finally:
        rover.cleanup()