import sys, os, time, adafruit_dht, board, smbus2, threading
from mouvements import goForward, initServos, scan
from mesures import mesures, ecriture
from app import app

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")

# Paramètres capteurs:
adresse = 0x40
bus = smbus2.SMBus(1)
try:
    capteur = adafruit_dht.DHT22(board.D25)
except AttributeError:
    capteur = None
    print("[main.py][DHT22] Capteur indisponible!")

# Lancement du serveur en arrière-plan:
flaskThread = threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
    daemon=True
)
flaskThread.start()
print("[main.py] Serveur démarré sur le port 5000!")

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
rover.init(0)
initServos()
print("[main.py] rover initialisé!")

# Main:
run = True
try:
    while run:
        # --- Bloc mesures ---
        
        distance.append(rover.getDistance())
        if len(distance) >= 5000:
            distance.pop(0)

        if time.time() >= lastMesure + intervalMesure:
            valeurs = mesures(adresse, capteur, bus)
            ecriture(adresse, capteur, bus, posX, posY)

            print(f"""
--- Mesures: ---                  
Temp: {valeurs['temperature']} {valeurs['unite_temp']} | Hum: {valeurs['humidite']} {valeurs['unite_hum']}
Distance: {int(distance[-1])}cm
            """)
            lastMesure = time.time()

            # Faux changements de position pour test du site:
            posX += 1
            if posX > 9:
                posX = 0
                posY += 1

        # --- Bloc déplacements ---

        if avancer == False:
            goForward(speed)
            avancer = True
            spinL = False
            spinR = False

        if all(x<=30 for x in distance[-5:]):
            rover.brake()
            avancer = False

            dirL, dirR = scan()
            print(f"""
--- Distances: ---
gauche = {dirL[-1]}cm
centre = {distance[-1]}cm
droite = {dirR}cm
""")

            if dirR[-1] > dirL[-1]:
                rover.spinRight(speed)
                spinR = True
                avancer = False
            else:
                rover.spinLeft(speed)
                spinL = True
                avancer = False
            
            while (max(distSpin[-10:]) - min(distSpin[-10:])) <= 1:
                distSpin.append(rover.getDistance())
                time.sleep(0.001)
            print(f"Finale: max = {max(distSpin[-10:])}cm | min = {min(distSpin[-10:])}")

            spinL = False
            spinR = False
            distSpin = []

        time.sleep(0.05)

finally: 
    rover.cleanup()