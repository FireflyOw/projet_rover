from __future__ import print_function
import time
import sys
import tty
import termios
import sys, os, time

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "capteurs"))

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

rover.init(0)
try:
    goForward(speed) 
    time.sleep(3)
    goLeft()
    time.sleep(3)
    goForward(speed)  
    time.sleep(3)
    goRight()
    time.sleep(3)
    goForward(speed)
finally : 
    rover.cleanup()
