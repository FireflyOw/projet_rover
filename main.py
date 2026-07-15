import time, sys, os, threading, pigpio, config.DHT22 as DHT22
from mouvements import goForward, initServos, scan
from mesures import mesures, ecriture, infosPi
from app import app

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "marsRover"))

try:
    import backups.marsRover.rover as rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import backups.marsRover.fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")

# ---- Démarrage serveur en arrière-plan: ----
flaskThread = threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
    daemon=True
)
flaskThread.start()
print("[main.py] Serveur démarré sur le port 5000!\n")

# ---- Paramètres mesure: ----
lastMesure = 0
intervalMesure = 3
valeurs = {}
distance = []
distSpin = []

# ---- Paramètres rover: ----
avancer = False
spinL = False
spinR = False
speed = 70
posX = 0
posY = 0

# ---- Initialisation rover: ----
rover.init(0)
initServos(rover)
print("[main.py] Rover initialisé!")

# ---- Initialisation capteurs: ----
SDA, SCL = 25, 5
adresse = 0x40

print("[main.py] Démarrage capteurs et bus I2C...")
pi = pigpio.pi()
try:
    pi.bb_i2c_close(SDA)
except pigpio.error:
    pass

# Ouverture du bus I2C:
pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)
print(f"[main.py] Bus I2C ouvert! SDA: {SDA}, SCL: {SCL}")

try:
    capteur = DHT22.sensor(pi, 24)
    print("[main.py][DHT22] Capteur initialisé!")
except (AttributeError, RuntimeError):
    print("[main.py][DHT22] Capteur non initialisé!")
    capteur = None

def mesuresBackground():
    global valeurs
    while True:
        mesureCapteurs = mesures(adresse, capteur, pi, SDA)
        mesurePi = infosPi()
        valeurs = { **mesureCapteurs, **mesurePi}

        print(f"\n{ecriture(valeurs, posX, posY)}")

        time.sleep(3)

distance.append(rover.getDistance())
time.sleep(0.05)

capteurThread = threading.Thread(target=mesuresBackground, daemon=True)
capteurThread.start()

# ---- Boucle principale : ----
run = True
try:
    while run:
        # --- Bloc mesures ---
        
        distance.append(rover.getDistance())
        if len(distance) >= 500:
            distance.pop(0)

        if time.time() >= lastMesure + intervalMesure:
            print(f"""
--- Mesures: ---                  
Temp: {valeurs.get('temperature', 'N/A')} | Hum: {valeurs.get('humidite', 'N/A')}
Particules: PM1 = {valeurs.get('pm1_atm', 'N/A')} | PM2.5 = {valeurs.get('pm1_atm', 'N/A')} | PM10 = {valeurs.get('pm1_atm', 'N/A')}
Distance: {float(distance[-1]):.1f}cm
--- Pi Zero infos: ---
CPU: {valeurs.get('cpu', 'N/A')}% ({valeurs.get('cpuTemp', 'N/A')}°C)
RAM: {valeurs.get('ramUsed', 'N/A')}MB / {valeurs.get('ramTotale', 'N/A')} MB ({valeurs.get('ramPercent', 'N/A')}%)""")
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

            print(f"""\nObstacle dans {distance[-1]:.2f}cm
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

            print(f"\nChemin trouvé! Prochain obstacle dans {distSpin[-1]:.2f}cm")

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
    print("\n[main.py] Nettoyage et fermeture...\n")
    rover.cleanup()
    try:
        pi.bb_i2c_close(SDA)
    except:
        pass