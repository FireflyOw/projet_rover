# -------------------- Importation des bibliothèques --------------------
#                           et fichiers utiles: 
# Bibliothèques
import time, sys, os, threading, pigpio, libraries.DHT22 as DHT22
# Fonctions des programmes annexes
from mouvements import initServos, goForward                                # Mouvements
from mesures import mesures, infosPi, ecriture, etalonnage , gyroscope      # Mesures
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

# Paramètres sonar
MAX_VALID_DISTANCE = 300
MAX_JUMP_CM = 20 
SONAR_DELAY = 0.03

# Fonctions pour le déplacement du rover sur la grille
def tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0):
   
    if sens == "droite":
        rover.spinRight(vitesse)
    elif sens == "gauche":
        rover.spinLeft(vitesse)
    else:
        raise ValueError("sens doit être 'droite' ou 'gauche'")
 
    angle_parcouru = 0.0
    dernier_temps = time.time()
    debut = dernier_temps
    compteur = 0

    while abs(angle_parcouru) < angle_cible:
        m = gyroscope(adresseMPU6050, pi, SDA, offsets, seuilGyro)
        maintenant = time.time()
        dt = maintenant - dernier_temps
        dernier_temps = maintenant 
        
        angle_parcouru += abs(m["gx"]) * dt

        compteur += 1
        if compteur % 10 == 0:  # affiche 1 fois sur 10 pour ne pas noyer la console
            print(f"gx={m['gx']:7.2f}  gy={m['gy']:7.2f}  gz={m['gz']:7.2f}  "
                  f"dt={dt*1000:5.1f}ms  angle_parcouru={angle_parcouru:6.2f}°")

        if maintenant - debut > timeout:
            print("[tourner] Timeout de sécurité atteint pendant le virage")
            break
 
        time.sleep(0.005)
 
    rover.brake()
    print(f"Nombre total de mesures effectuées : {compteur}")

def demitour_D(offsets):
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(rover, speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)  

def demitour_G(offsets):
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(rover, speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)

def lire_distance_brute():
    d = rover.getDistance()
    if d > MAX_VALID_DISTANCE:
        return None
    return d

def SonarDistance(taille_case=30):
    d1 = None
    while d1 is None:
        d1 = lire_distance_brute()
        time.sleep(SONAR_DELAY)
    goForward(rover, speed)

    derniere_distance_valide = d1

    while True:
        d = lire_distance_brute()
        time.sleep(SONAR_DELAY)

        if d is None:
            continue

        # Rejet des sauts physiquement impossibles (bruit ponctuel isolé)
        if abs(d - derniere_distance_valide) > MAX_JUMP_CM:
            print(f"Mesure rejetée (saut trop important) : {d:.1f} cm")
            continue

        derniere_distance_valide = d
        print(d)

        if abs(d1 - d) >= taille_case:
            rover.brake()
            print("case atteinte")
            break

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

pi.bb_i2c_zip(SDA, [4, adresseMPU6050, 2, 7, 2, 0x6B, 0x00, 3, 0])
time.sleep(0.3)

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
            demitour_D(offsets)
            y +=1

            # Même principe que précédemment, mais dans l'autre sens
            while posX !=0:
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

                posX -= 1

            # Une fois la ligne complètée, on fait demi-tour dans l'autre sens
            demitour_G(offsets)
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