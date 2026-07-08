import sys, os, time, adafruit_dht, board, smbus2
from mouvements import goForward, evitement, speed
from mesures import mesures, ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[mouvements.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

# Paramètres capteurs:
adresse = 0x40
bus = smbus2.SMBus(1)
try:
    capteur = adafruit_dht.DHT22(board.D25)
except AttributeError:
    capteur = None
    print("[DHT22] Capteur indisponible!")

# Paramètres mesure:
lastMesure = 0
intervalMesure = 3
distance = []

# ---- Boucle test : ----
rover.init(0)

# Main:
run = True
try:
    while run:
        distance.append(rover.getDistance())
        if len(distance) >= 10000:
            distance.pop(0)

        if time.time() >= lastMesure + intervalMesure:
            valeurs = mesures(adresse, capteur, bus)
            print(f"Temp: {valeurs['temperature']} {valeurs['unite_temp']} | Hum: {valeurs['humidite']} {valeurs['unite_hum']}")
            print(f"Distance: {int(distance[-1])}cm")
            lastMesure = time.time()

finally: 
    run = False
    rover.cleanup()