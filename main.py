import time, sys, os, threading, flask, pigpio, config.DHT22 as DHT22
from mouvements import goForward, initServos, scan
from mesures import mesures, ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "marsRover"))

try:
    import backups.marsRover.rover as rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import backups.marsRover.fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")


# Initialisation rover:
rover.init(0)
initServos(rover)
print("[main.py] rover initialisé!")

# Paramètres capteurs:
adresse = 0x40
try:
    pi = pigpio.pi()
    capteur = DHT22.sensor(pi, 24)
    print("[main.py][DHT22] Capteur initialisé!\n")
except AttributeError:
    print("[main.py][DHT22] Capteur non initialisé!\n")
    capteur = None

# Paramètres mesure:
lastMesure = 0
intervalMesure = 3
distance = []
distSpin = []

# Paramètres rover:
avancer = False
spinL = False
spinR = False
speed = 70
posX = 0
posY = 0

# ---- Boucle principale : ----
run = True
try:
    while run:
        # --- Bloc mesures ---
        
        distance.append(rover.getDistance())
        if len(distance) >= 500:
            distance.pop(0)

        if time.time() >= lastMesure + intervalMesure:
            valeurs = mesures(adresse, capteur, rover.bus)
            ecriture(valeurs, posX, posY)

            print(f"""
--- Mesures: ---                  
Temp: {valeurs['temperature']} {valeurs['unite_temp']} | Hum: {valeurs['humidite']} {valeurs['unite_hum']}
Particules: PM1 = {valeurs['pm1_atm']} {valeurs['unite']} | PM2.5 = {valeurs['pm1_atm']} {valeurs['unite']} | PM10 = {valeurs['pm1_atm']} {valeurs['unite']}
Distance: {float(distance[-1]):.1f}cm
            """)
            lastMesure = time.time()

            # Faux changements de position pour test du site:
            posX += 1
            if posX > 9:
                posX = 0
                posY += 1

        # --- Bloc déplacements ---

        if all(x<=30 for x in distance[-5:]):
            rover.brake()
            avancer = False

            print(f"""Obstacle dans {distance[-1]:.2f}cm
Scanning.....""")
            
            dirL, dirR = scan(rover)

            print(f"""
--- Distances: ---
gauche = {dirL:.2f}cm
centre = {distance[-1]:.2f}cm
droite = {dirR:.2f}cm\n""")
            
            if dirR > dirL:
                rover.spinRight(speed)
                spinR = True
                avancer = False
            else:
                rover.spinLeft(speed)
                spinL = True
                avancer = False

            while len(distSpin) < 10 or ((max(distSpin) - min(distSpin)) > 2 and distSpin[-1] > 50):
                distSpin.append(rover.getDistance())
                time.sleep(0.05)

                if len(distSpin) > 10:
                    distSpin.pop(0)

            print(f"Chemin trouvé! Prochain obstacle dans {distSpin[-1]:.2f}cm\n")

            rover.stop()
            spinL = False
            spinR = False
            distSpin = []

        if avancer == False:
            goForward(rover, speed)
            avancer = True
            spinL = False
            spinR = False

        time.sleep(0.05)

finally: 
    rover.cleanup()