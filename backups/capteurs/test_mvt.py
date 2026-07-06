from __future__ import print_function
import time
import sys
import sys, os, time

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rover"))

try:
    import rover
    print("[mouvement.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0
speed = 60

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

def init_servo():
    rover.setServo(servo_Avant_G, 0)
    time.sleep(0.01)
    rover.setServo(servo_Avant_D, 0)
    time.sleep(0.01)
    rover.setServo(servo_Arrière_G, 0)
    time.sleep(0.01)
    rover.setServo(servo_Arrière_D, 0)
    time.sleep(0.01)
    rover.setServo(servo_Sonar, 0)

def evitement():
    goRight()
    print("blabla")
    time.sleep(3)

rover.init(0)


init_servo()
time.sleep(2)

rover.setServo(servo_Sonar, 84)
time.sleep(0.5)
rover.setServo(servo_Sonar, -84)
time.sleep(0.5)
rover.setServo(servo_Sonar, 84)
time.sleep(0.5)
rover.setServo(servo_Sonar, -84)
time.sleep(0.5)

stepSpinL()
init_servo()

print("bloblo")
rover.cleanup()





#distance = []
#run = True
#try:
#    while run:
#        distance.append(rover.getDistance())
#
#        print(distance[-1:])
#        goForward(speed)
#        if all(x<=35 for x in distance[-5:]):
#            evitement()
#            run = False
    
#finally: 
#    rover.cleanup()



