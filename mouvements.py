import sys, os, time, adafruit_dht, adafruit_blinka, board, smbus2
from mesures import temp_hum
from __future__ import print_function
import termios, tty

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[mouvements.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

# Paramètres capteurs:
adresse = 0x40
bus = smbus2.SMBus(1)
capteur = adafruit_dht.DHT22(board.D12)

# Paramètres rover:
servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0

speed = 60


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


# Boucle test :
rover.init(0)

lastPrint = 0
intervalPrint = 2
distance = []
run = True

try:
    while run:
        tempHum = temp_hum(capteur, bus)
        distance.append(rover.getDistance())

        if time() >= lastPrint + intervalPrint:
            print(f"Distance: {distance[-1:]} cm")
            print(f"Temp: {tempHum["temperature"]} {tempHum["unite_temp"]} | Hum: {tempHum["humidite"]} {tempHum["unite_hum"]}")
            lastPrint = time()
        
        goForward(speed)
        
        if all(x<=35 for x in distance[-5:]):
            evitement()
            run = False

finally: 
    rover.cleanup()