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
speed = 50

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
        now=time.time()
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
        


        if all(x<=30 for x in distance[-5:]):
            while all(int(distance[-1]) -1 <x and x<  int(distance[-1]) +1 for x in distance[-5:]):
                distance.append(rover.getDistance())
                time.sleep(0.001)
                print(distance[-1:])
                
                if Spin==False:
                    rover.spinLeft(70)
                    Spin=True
                    Av=False
                print("bloblo")
            
            

        time.sleep(0.001)

    
finally: 
   rover.cleanup()
   print(len(distance))



