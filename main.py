# -------------------- Importation des bibliothèques --------------------
#                           et fichiers utiles: 
# Bibliothèques
import time, sys, os, threading, pigpio, libraries.DHT22 as DHT22
# Fonctions des programmes annexes
from mouvements import initServos, SonarDistance, demitour_D, demitour_G    # Mouvements
from mesures import mesures, infosPi, ecriture, etalonnage                  # Mesures
from app import app                                                         # Serveur
# Bibliothèque et fonctions écran
from backups.ecran.ecran import gestionI2C
from luma.oled.device import ssd1306
from luma.core.render import canvas

# -------------------- Importation des fichiers rover: --------------------
sys.path.append(os.path.join(os.path.dirname(__file__), "marsRover"))

import marsRover.rover as rover

# -------------------- Démarrage serveur en arrière-plan: --------------------
flaskThread = threading.Thread(
    target=lambda: app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False),
    daemon=True
)
flaskThread.start()
print("[main.py] Serveur démarré sur le port 5000!\n")

# -------------------- Paramètres rover: --------------------
speed = 70
posX = 0
posY = 0
y = 3
x = 3

# -------------------- Initialisation rover: --------------------
rover.init(0)
initServos(rover)
print("[main.py] Rover initialisé!")

# -------------------- Initialisation capteurs et I²C: --------------------
SDA, SCL = 25, 5

adresseHM3301 = 0x40
adresseMPU6050 = 0x68

print("[main.py] Démarrage capteurs, thread et bus I2C...")

pi = pigpio.pi()

# Sécurité pour ne pas laisser d'ancien bus ouvert
try:
    pi.bb_i2c_close(SDA)
except pigpio.error:
    pass

# Ouverture du nouveau bus
pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)
print(f"[main.py] Bus I2C ouvert! SDA: {SDA}, SCL: {SCL}")

valeurs = {}

# Initialisation propre du DHT22
try:
    capteur = DHT22.sensor(pi, 24)
    print("[main.py][DHT22] Capteur initialisé!")
except (AttributeError, RuntimeError):
    print("[main.py][DHT22] Capteur non initialisé...")
    capteur = None

# Étalonnage du gyroscope
offsets = etalonnage(adresseMPU6050, pi, SDA)
time.sleep(0.5)

# -------------------- Initialisation écran: --------------------
adresseOLED = 0x3C
interfaceI2C = gestionI2C(pi, SDA, address=adresseOLED)
ecran = ssd1306(interfaceI2C, width=128, height=32, rotate=0)


# -------------------- Boucle principale : --------------------
try:
    while True:
        with canvas(ecran) as draw:
            draw.text((0, 0), ">> DEPLACEMENT EN COURS", fill="white")
            draw.text((0, 20), f"Pos: X={posX} ; Y={posY} | V=70%", fill="white")
    
        # Déplacement par pas de 50cm
        SonarDistance()

        # ---- Arrêt pour mesure ----
        rover.brake()

        with canvas(ecran) as draw:
            draw.text((0, 0), f"MESURE --> X={posX} ; Y={posY}", fill="white")

        mesureCapteurs = mesures(adresseHM3301, capteur, pi, SDA)
        mesurePi = infosPi()
        
        valeurs.clear()
        valeurs.update({ **mesureCapteurs, **mesurePi})

        print(f"""
--- Mesures environnementales: ---                  
Temp: {valeurs.get('temperature', 'N/A')}{valeurs.get('uniteTemp')} | Hum: {valeurs.get('humidite', 'N/A')}{valeurs.get('uniteHum')}
Particules: PM1 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM2.5 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM10 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')}
--- Pi Zero infos: ---
CPU: {valeurs.get('cpu', 'N/A')}% ({valeurs.get('cpuTemp', 'N/A')}°C)
RAM: {valeurs.get('ramUsed', 'N/A')}MB / {valeurs.get('ramTotale', 'N/A')} MB ({valeurs.get('ramPercent', 'N/A')}%)""")
        
        print(f"\n{ecriture(valeurs, posX, posY)}")

        with canvas(ecran) as draw:
            draw.text((0, 0), f"MESURE --> X={posX} ; Y={posY}", fill="white")
            draw.text((0, 20), f"T={valeurs["temperature"]}°C | H={valeurs["humidite"]}% | Pi={valeurs["cpu"]}°C", fill="white")

        time.sleep(1)  

        # Incrémentation de la position x
        posX += 1
        # Si on a complété la grille, on arrête le programme
        if x==posX and y==posY:
            break

        # Si on est en bout de ligne, le rover fait un demi-tour
        if x==posX:
            demitour_D(speed, offsets)
            y +=1

            # Même principe que précédemment, mais dans l'autre sens
            while posX !=0:
                SonarDistance(speed, rover)

                # ---- Arrêt pour mesure ----
                rover.brake()
                with canvas(ecran) as draw:
                    draw.text((0, 0), f"MESURE --> X={posX} ; Y={posY}", fill="white")

                mesureCapteurs = mesures(adresseHM3301, capteur, pi, SDA)
                mesurePi = infosPi()

                valeurs.clear()
                valeurs.update({ **mesureCapteurs, **mesurePi})

                print(f"""
                --- Mesures environnementales: ---                  
                Temp: {valeurs.get('temperature', 'N/A')}{valeurs.get('uniteTemp')} | Hum: {valeurs.get('humidite', 'N/A')}{valeurs.get('uniteHum')}
                Particules: PM1 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM2.5 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')} | PM10 = {valeurs.get('pm1_atm', 'N/A')} {valeurs.get('uniteAir')}
                --- Pi Zero infos: ---
                CPU: {valeurs.get('cpu', 'N/A')}% ({valeurs.get('cpuTemp', 'N/A')}°C)
                RAM: {valeurs.get('ramUsed', 'N/A')}MB / {valeurs.get('ramTotale', 'N/A')} MB ({valeurs.get('ramPercent', 'N/A')}%)""")

                print(f"\n{ecriture(valeurs, posX, posY)}") 

                with canvas(ecran) as draw:
                    draw.text((0, 0), f"MESURE --> X={posX} ; Y={posY}", fill="white")
                    draw.text((0, 20), f"T={valeurs["temperature"]}°C | H={valeurs["humidite"]}% | Pi={valeurs["cpu"]}°C", fill="white")

                time.sleep(1)

                posX -= 1

            # Une fois la ligne complètée, on fait demi-tour dans l'autre sens
            demitour_G(speed, offsets)
            posY += 1

        # Si on a complété la grille, on arrête le programme
        if x==posX and y==posY:
            break

except KeyboardInterrupt:
    pass

finally: 
    print("\n[main.py] Nettoyage et fermeture...\n")
    rover.cleanup()
    try:
        pi.bb_i2c_close(SDA)
    except:
        pass