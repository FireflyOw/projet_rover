from __future__ import print_function
import sys, os, time, adafruit_dht, board, smbus2
from mesures import temp_hum

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[mouvements.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

# Paramètres rover:
rover.init(0)

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0

speed = 60

# Paramètres capteurs:
adresse = 0x40
bus = smbus2.SMBus(1)
capteur = adafruit_dht.DHT22(board.D25)

# Mouvements rover:
def goForward(speed):
    rover.setServo(servo_Avant_G, 0)
    rover.setServo(servo_Avant_D, 0)
    rover.setServo(servo_Arrière_G, 0)
    rover.setServo(servo_Arrière_D, 0)
    rover.forward(speed)

def goReverse(speed):
    rover.setServo(servo_Avant_G, 0)
    rover.setServo(servo_Avant_D, 0)
    rover.setServo(servo_Arrière_G, 0)
    rover.setServo(servo_Arrière_D, 0)
    rover.reverse(speed)

def goLeft():
    rover.setServo(servo_Avant_G, -20)
    rover.setServo(servo_Avant_D, -20)
    rover.setServo(servo_Arrière_G, 20)
    rover.setServo(servo_Arrière_D, 20)

def goRight():
    rover.setServo(servo_Avant_G, 20)
    rover.setServo(servo_Avant_D, 20)
    rover.setServo(servo_Arrière_G, -20)
    rover.setServo(servo_Arrière_D, -20)

def evitement():
    goRight()
    print("blabla")
    time.sleep(3)


# ---- Boucle test : ----

# Paramètres mesure:
lastMesure = 0
intervalMesure = 3
distance = []

# Main:
run = True
try:
    while run:
        distance.append(rover.getDistance())

        if len(distance) >= 5 and all(x<=35 for x in distance[-5:]):
            rover.brake()
            evitement()
            distance.clear()
            run = False
        else:
            goForward(speed)

        if time.time() >= lastMesure + intervalMesure:
            tempHum = temp_hum(capteur)
            print(f"Distance: {distance[-1:]} cm")
            print(f"Temp: {tempHum["temperature"]} {tempHum["unite_temp"]} | Hum: {tempHum["humidite"]} {tempHum["unite_hum"]}")
            lastMesure = time.time()

finally: 
    rover.cleanup()