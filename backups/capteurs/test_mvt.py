from __future__ import print_function
import time
import sys, os, time

dossier = os.path.dirname(__file__)
racineProjet = os.path.abspath(os.path.join(dossier, "..", "marsRover"))
sys.path.append(racineProjet)

import backups.marsRover.rover as rover

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0
speed = 100

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

# def getValidDistance():
#                 d = rover.getDistance()
#                 if d > MAX_VALID_DISTANCE:
#                     return None  
#                 return d


# Evitement

# rover.init(0)
# init_servo()
# time.sleep(1)

# Av = False
# Spin =False
# non = 0
# now = 0
# distance = []
# spin_speed = 80
# MAX_VALID_DISTANCE = 300 
# MAX_TURN_DURATION = 5.0

# try:
#    while True:
#         distance.append(rover.getDistance())
#         print(distance[-1:])

#         if Av==False:
#             goForward(speed)
#             Av=True            
#             Spin=False

   
#         if all(x<=30 for x in distance[-5:]):
#             print("blabla")
#             rover.stop()
#             spin_speed = 80
#             direction_G =[]
#             rover.setServo(servo_Sonar, -84)
#             direction_G.append(rover.getDistance())
#             time.sleep(2)
#             direction_D =[]
#             rover.setServo(servo_Sonar, 84)
#             direction_D.append(rover.getDistance())
#             time.sleep(2)
#             rover.setServo(servo_Sonar, 0)


#             if direction_D[-1]>direction_G[-1]:
#                 spin_func = rover.spinRight
                
#             else:
#                 spin_func = rover.spinLeft

#             spin_func(spin_speed)
#             Spin = True
#             Av = False

#             turn_readings = []
#             slowed = False
#             turn_start = time.time()
            
#             far_readings_count = 0
#             REQUIRED_CONSECUTIVE = 3

#             while True:

#                 d = rover.getDistance() 
#                 print(d)

#                 if d <= MAX_VALID_DISTANCE:
#                     distance.append(d)
#                     turn_readings.append(d)

#                     if d > 80:
#                         far_readings_count += 1
#                     else:
#                         far_readings_count = 0

#                 if not slowed and far_readings_count > REQUIRED_CONSECUTIVE:
#                     print("ralentissement")
#                     spin_speed = 26.5
#                     spin_func(spin_speed)  
#                     slowed = True

                
#                 if len(turn_readings) >= 10:
#                     window = turn_readings[-25:]
#                     if (max(window) - min(window)) <= 1.5:
#                         break
                
#                 if time.time() - turn_start > MAX_TURN_DURATION:
#                     print("timeout de sécurité - sortie forcée")
#                     break

#                 time.sleep(0.01)

#             Spin = False


    
# finally: 
#    print(len(distance))
#    rover.cleanup()



rover.init(0)
init_servo()
time.sleep(1)

goForward(speed)
time.sleep(1.5)
rover.brake()
time.sleep(1.5)
goForward(speed)
time.sleep(1.5)
rover.brake()
time.sleep(1.5)
goForward(speed)
time.sleep(1.5)
rover.brake()
time.sleep(1.5)
rover.spinLeft(speed)
time.sleep(1.5)

rover.cleanup()