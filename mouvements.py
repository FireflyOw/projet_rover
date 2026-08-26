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