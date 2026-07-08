from __future__ import print_function
import time
import sys
import sys, os, time
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "rover"))
import rover

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0
speed = 80

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


init_servo()
time.sleep(2)

# rover.setServo(servo_Sonar, 84)
# time.sleep(0.5)
# rover.setServo(servo_Sonar, -84)
# time.sleep(0.5)
# rover.setServo(servo_Sonar, 84)
# time.sleep(0.5)
# rover.setServo(servo_Sonar, -84)
# time.sleep(0.5)

Av = False
Spin =False
non = 0
now = 0
rover.init(0)
distance = []
try:
   while True:
        distance.append(rover.getDistance())
        print(distance[-1:])

        if Av==False:
            goForward(speed)
            Av=True            
            Spin=False


        # if non<=now +4:
        #     rover.setServo(servo_Sonar, 84)
        #     time.sleep(0.5)
        #     rover.setServo(servo_Sonar, -84)
        #     time.sleep(0.5)
        #     rover.setServo(servo_Sonar, 0)
        #     non = time.time()
        

#aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
        if all(x<=30 for x in distance[-5:]):
            print("blabla")
            rover.spinLeft(30)
            Spin=True
            Av=False

            turn_readings = []

            while True:
                distance.append(rover.getDistance())
                turn_readings.append(rover.getDistance())
                print("bloblo", rover.getDistance())
                
                if len(turn_readings) >= 10:
                    window = turn_readings[-10:]
                    if (max(window) - min(window)) <= 1:
                        break
                
                time.sleep(0.01)
            Spin = False


    
finally: 
   print(len(distance))
   rover.cleanup()


