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

# ---- Initialisation rover: ----
rover.init(0)
initServos(rover)
print("[main.py] Rover initialisé!")

# ---- Paramètres mesure: ----
distance = []
distSpin = []

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