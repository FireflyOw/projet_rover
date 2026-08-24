from __future__ import print_function
from mesures import gyroscope
from main import pi, SDA
import time

# Paramètres rover:
servoAvG = 9
servoAvD = 15
servoArG = 11
servoArD = 13
servoSonar = 0

# Paramètres sonar
MAX_VALID_DISTANCE = 300
MAX_JUMP_CM = 8
SONAR_DELAY = 0.03

# Fonction pour estimer la vitesse de déplacement du rover:
def calculVitesse(speed):
    vMaxTheorique = 17.6
    vSeuil = 26
    
    if abs(speed) < vSeuil:
        return 0.0
    
    puissance = (abs(speed) - vSeuil) / (100 - vSeuil)
    vitesse = puissance * vMaxTheorique

    return round(vitesse, 2)
    
# Fonction d'initialisation des servos (mis à 0):
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

# Fonctions pour le déplacement du rover sur la grille
def tourner_90(rover, adresse, offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0):
   
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
        m = gyroscope(adresse, pi, SDA, offsets, seuilGyro, seuilGyro)
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

def demitour_D(speed, offsets):
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)  

def demitour_G(speed, offsets):
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)

def lire_distance_brute(rover):
    d = rover.getDistance()
    if d > MAX_VALID_DISTANCE:
        return None
    return d

def SonarDistance(speed, rover, taille_case=30):
    d1 = None
    while d1 is None:
        d1 = lire_distance_brute()
        time.sleep(SONAR_DELAY)
    goForward(speed)

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