from __future__ import print_function
import sys, os, time

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[mouvements.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

# Paramètres rover:
servoAvG = 9
servoAvD = 15
servoArG = 11
servoArD = 13
servoSonar = 0

# Fonction d'initialisation des servos (mis à 0):
def initServos():
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.setServo(servoSonar, 0)
    
# Mouvements du rover:
def goForward(speed):
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.forward(speed)

def goReverse(speed):
    rover.setServo(servoAvG, 0)
    rover.setServo(servoAvD, 0)
    rover.setServo(servoArG, 0)
    rover.setServo(servoArD, 0)
    rover.reverse(speed)

def goLeft():
    rover.setServo(servoAvG, -20)
    rover.setServo(servoAvD, -20)
    rover.setServo(servoArG, 20)
    rover.setServo(servoArD, 20)

def goRight():
    rover.setServo(servoAvG, 20)
    rover.setServo(servoAvD, 20)
    rover.setServo(servoArG, -20)
    rover.setServo(servoArD, -20)

# Gestion d'obstacles:

def scan():
    dirL = []
    dirR = []

    rover.setServo(servoSonar, -84)
    dirL.append(rover.getDistance())
    time.sleep(2)    
    rover.setServo(servoSonar, 84)
    dirR.append(rover.getDistance())
    time.sleep(2)
    rover.setServo(servoSonar, 0)

    return dirL, dirR