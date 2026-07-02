from __future__ import print_function
import rover, time
import sys
import tty
import termios
import sys, os, time


try:
    import rover
    print("[mouvement.py] rover.py chargé (Raspberry Pi Zero)")
except ModuleNotFoundError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0
speed = 60
def goForward():
    rover.setServo(servo_Avant_G, 0)
    rover.setServo(servo_Avant_D, 0)
    rover.setServo(servo_Arrière_G, 0)
    rover.setServo(servo_Arrière_D, 0)
    rover.forward(speed)

def goReverse():
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



path = [
    (goForward, 3),   
    (goLeft,    1.5), 
    (goForward, 2),   
    (goRight,   1.5),
    (goForward, 3),  
]