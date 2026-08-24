import sys, os, time
from __future__ import print_function

dossier = os.path.dirname(__file__)
racineProjet = os.path.abspath(os.path.join(dossier, "..", ".."))
dirMarsRover = os.path.join(racineProjet, "backups", "marsRover")

sys.path.append(racineProjet)
sys.path.append(dirMarsRover)

import marsRover.rover as rover

# Initialisation des servos:
def initServos(rover):
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.setServo(servoSonar, 0)
    
# Mouvements du rover:
def goForward(rover, speed):
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.forward(speed)

def goReverse(rover, speed):
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.reverse(speed)

def goLeft(rover):
    rover.setServo(servoAvG, -20)
    rover.setServo(servoAvD, -20)
    rover.setServo(servoArG, 20)
    rover.setServo(servoArD, 20)

def goRight(rover):
    rover.setServo(servoAvG, 20)
    rover.setServo(servoAvD, 20)
    rover.setServo(servoArG, -20)
    rover.setServo(servoArD, -20)

# Gestion d'obstacles:
def scan(rover):
    rover.setServo(servoSonar, -84)
    time.sleep(1)
    dirL = rover.getDistance()
    time.sleep(0.05)
    rover.setServo(servoSonar, 84)
    time.sleep(1)
    dirR = rover.getDistance()
    time.sleep(0.05)
    rover.setServo(servoSonar, 0)

    return dirL, dirR

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
        m = gyroscope(adresse, offsets, seuilGyro)
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

def evitement(offsets) :
# Le rover a détecté un obstacle
    dirL, dirR = scan(rover)

    # On choisi le côté le plus dégagé
    if dirR > dirL:
        tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)
        spinR = True
    else:
        tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)
        spinL = True

    # Retour sur la case selon si on a tourné à gauche ou à droite au départ
    if spinL :
        spinL = False

        # Sonar à droite pour regarder si on a passé l'obstacle
        rover.setServo(servoSonar, 84)
        distanceInitiale = 0
        distanceFinale = 0
        while distance[-1] < 50 :
            distanceInitiale = rover.getDistance()
            distance.append(rover.getDistance())
            goForward(speed) # On avance tant qu'on a pas passé l'obstacle

        distanceFinale = rover.getDistance()
        distanceParcourue = distanceFinale - distanceInitiale
        tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)

        while distance[-1] < 50 :
            distance.append(rover.getDistance())
            goForward(speed) # On avance tant qu'on a pas passé l'obstacle
        
        rover.setServo(servoSonar, 0)
        tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)

        nouvelleDistance = rover.getDistance()

        while distance[-1] - nouvelleDistance < distanceParcourue :
            distance.append(rover.getDistance())
            goForward(speed)

    else :
        spinR = False 

        distanceInitiale = rover.getDistance()
        # Sonar à gauche pour regarder si on a passé l'obstacle
        rover.setServo(servoSonar, -84)
        while distance[-1] < 50 :
            distance.append(rover.getDistance())
            goForward(speed) # On avance tant qu'on a pas passé l'obstacle

        rover.setServo(servoSonar, 0)
        distanceFinale = rover.getDistance()
        distanceParcourue = distanceFinale - distanceInitiale
        tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)

        rover.setServo(servoSonar, -84)
        while distance[-1] < 50 :
            distance.append(rover.getDistance())
            goForward(speed) # On avance tant qu'on a pas passé l'obstacle
        
        rover.setServo(servoSonar, 0)
        tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)

        nouvelleDistance = rover.getDistance()

        while distance[-1] - nouvelleDistance < distanceParcourue :
            distance.append(rover.getDistance())
            goForward(speed)

def lecture(h, l):
    valeur = (h << 8) | l
    return valeur - 65536 if valeur >= 0x8000 else valeur

def gyroscope(adresse, pi, SDA, offsets, seuilGyro = 0.2):
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur mesure: lecture incomplète, {count}/14 octets reçus!")
    else:
        ax = round(lecture(data[0], data[1]) / 16384.0 - offsets["ax"], 2)
        ay = round(lecture(data[2], data[3]) / 16384.0 - offsets["ay"], 2)
        az = round(lecture(data[4], data[5]) / 16384.0 - offsets["az"], 2)
        
        gx = round(lecture(data[8], data[9]) / 131.0   - offsets["gx"], 2)
        gy = round(lecture(data[10], data[11]) / 131.0 - offsets["gy"], 2)
        gz = round(lecture(data[12], data[13]) / 131.0 - offsets["gz"], 2)

        gx = 0.0 if abs(gx) < seuilGyro else gx
        gy = 0.0 if abs(gy) < seuilGyro else gy
        gz = 0.0 if abs(gz) < seuilGyro else gz

    return {"ax": ax, "ay": ay, "az": az,
            "gx": gx, "gy": gy, "gz": gz,}

def etalonnage(adresse, pi, SDA, echantillons = 100):
    print(f"[MPU6050] Étalonnage en cours... Ne pas bouger le rover ({echantillons} mesures)")

    sum_ax, sum_ay, sum_az = 0, 0, 0
    sum_gx, sum_gy, sum_gz = 0, 0, 0
    lecturesValides = 0

    while lecturesValides < echantillons:
        count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

        if count < 14:
            raise RuntimeError(f"Erreur étalonnage: mesure n°{lecturesValides + 1} invalide, {count}/14 octets reçus!")
        else:
            sum_ax += lecture(data[0], data[1]) / 16384.0
            sum_ay += lecture(data[2], data[3]) / 16384.0
            sum_az += lecture(data[4], data[5]) / 16384.0
            
            sum_gx += lecture(data[8], data[9]) / 131.0
            sum_gy += lecture(data[10], data[11]) / 131.0
            sum_gz += lecture(data[12], data[13]) / 131.0

        lecturesValides += 1
        time.sleep(0.01)
        
    offsets = {
    "ax": (sum_ax / lecturesValides) - 1.0,
    "ay": (sum_ay / lecturesValides) - 0.0,
    "az": (sum_az / lecturesValides) - 0.0,

    "gx": (sum_gx / lecturesValides) - 0.0,
    "gy": (sum_gy / lecturesValides) - 0.0,
    "gz": (sum_gz / lecturesValides) - 0.0,
    }

    print(f"[MPU6050] Étalonnage terminé ! Offsets calculés : {offsets}")

    return offsets

# ---- Initialisation rover: ----
rover.init(0)
initServos(rover)
print("[main.py] Rover initialisé!")

# ---- Paramètres mesure: ----
distance = []
distSpin = []
adresse = 0x68

# ---- Paramètres rover: ----
servoAvG = 9
servoAvD = 15
servoArG = 11
servoArD = 13
servoSonar = 0
avancer = False
spinL = False
spinR = False
speed = 70

# ---- Boucle principale : ----
run = True
try:
    while run:
        distance.append(rover.getDistance())
        if len(distance) >= 500:
            distance.pop(0)

        # Obstacle détecté
        if all(x<=30 for x in distance[-5:]):
            rover.brake()
            evitement()

        time.sleep(0.05)

finally: 
    print("\n[main.py] Nettoyage et fermeture...\n")
    rover.cleanup()