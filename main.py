import time, sys, os, threading, pigpio, config.DHT22 as DHT22
from mouvements import calculVitesse, goForward, initServos, scan
from mesures import mesures, infosPi, ecriture
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
width = 3
lenght = 3
tempsMesure = 3
tolerance = 1
deplacement = 0
distanceMax = 100
distanceMesure = 10
nouvelleMesure = True
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

print("[main.py] Démarrage capteurs, thread et bus I2C...")
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
    print("[main.py][DHT22] Capteur non initialisé...")
    capteur = None

distance.append(rover.getDistance())

time.sleep(2)
nouvelleMesure = False
print("[main.py] Thread démarré!")

# ---- Boucle principale : ----
try:
    while posY < width:
        # --- Bloc mesures ---
        
        distance.append(rover.getDistance())
        if len(distance) >= 500:
            distance.pop(0)

        if nouvelleMesure:
            mesureCapteurs = mesures(adresse, capteur, pi, SDA)
            mesurePi = infosPi()
            
            valeurs.clear()
            valeurs.update({ **mesureCapteurs, **mesurePi})

            posX += 1
            if posX > lenght:
                posX = 0
                posY += 1
                
            print(f"""
--- Mesures: ---                  
Temp: {valeurs.get('temperature', 'N/A')}{valeurs.get('uniteTemp')} | Hum: {valeurs.get('humidite', 'N/A')}{valeurs.get('uniteHum')}
Particules: PM1 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM2.5 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM10 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')}
Distance: {float(distance[-1]):.1f}cm
--- Pi Zero infos: ---
CPU: {valeurs.get('cpu', 'N/A')}% ({valeurs.get('cpuTemp', 'N/A')}°C)
RAM: {valeurs.get('ramUsed', 'N/A')}MB / {valeurs.get('ramTotale', 'N/A')} MB ({valeurs.get('ramPercent', 'N/A')}%)""")
            
            print(f"\n{ecriture(valeurs, posX, posY)}")
            nouvelleMesure = False

        # --- Bloc déplacements ---

        if avancer == False and nouvelleMesure == False:
            goForward(rover, speed)
            avancer = True
            spinL = False
            spinR = False
        
        if abs((distanceMax - distance[-1]) - deplacement) <= tolerance:
            rover.brake()
            nouvelleMesure = True
            deplacement += distanceMesure

        time.sleep(0.05)

finally: 
    print("\n[main.py] Nettoyage et fermeture...\n")
    rover.cleanup()
    try:
        pi.bb_i2c_close(SDA)
    except:
        pass