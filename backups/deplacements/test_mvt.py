from __future__ import print_function
import sys, os, time, pigpio

dossier = os.path.dirname(__file__)
racineProjet = os.path.abspath(os.path.join(dossier, "..", ".."))
dirMarsRover = os.path.join(racineProjet, "backups", "marsRover")

sys.path.append(racineProjet)
sys.path.append(dirMarsRover)

import marsRover.rover as rover

servo_Avant_G = 9
servo_Avant_D = 15
servo_Arrière_G = 11
servo_Arrière_D = 13
servo_Sonar = 0
speed = 100
#--------------------------------------------------------------Fonctions_Mouvement------------------------------------------------------------------------------
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

rover.init(0)
init_servo()
time.sleep(1)

#---------------------------------------------------- Fonctions pour gyro + accéléromètre -------------------------------------------------------------------
SDA, SCL = 25, 5
adresse = 0x68

pi = pigpio.pi()

try:
    pi.bb_i2c_close(SDA)
except pigpio.error:
    pass

pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)

pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 2, 0x6B, 0x00, 3, 0])
time.sleep(0.3)

def lecture(h, l):
    v = (h << 8) | l
    return v - 65536 if v >= 0x8000 else v

def mesure(adresse, offsets, seuilGyro = 0.5):
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur mesure: lecture incomplète, {count}/14 octets reçus!")
    else:
        ax = round(lecture(data[0], data[1]) / 16384.0 - offsets["ax"], 2)
        ay = round(lecture(data[2], data[3]) / 16384.0 - offsets["ay"], 2)
        az = round(lecture(data[4], data[5]) / 16384.0 - offsets["az"], 2)
        
        gx = round(lecture(data[8], data[9]) / 131.0   - offsets["gx"], 2)
        gy = round(lecture(data[10], data[11]) / 131.0 - offsets["gy"], 2)
        gz = round(lecture(data[12], data[13]) / 131.0 - offsets["gz"], 2)

        gx = 0.0 if abs(gx) < seuilGyro else gx
        gy = 0.0 if abs(gy) < seuilGyro else gy
        gz = 0.0 if abs(gz) < seuilGyro else gz

    return {"ax": ax, "ay": ay, "az": az,   
            "gx": gx, "gy": gy, "gz": gz,}


#-------------------------------------------------------------Etalonnage-------------------------------------------------------------------------------------




def etalonnage(adresse, echantillons = 100):
    print(f"[MPU6050] Étalonnage en cours... Ne pas bouger le rover ({echantillons} mesures)")

    sum_ax, sum_ay, sum_az = 0, 0, 0
    sum_gx, sum_gy, sum_gz = 0, 0, 0
    lecturesValides = 0

    while lecturesValides < echantillons:
        count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

        if count < 14:
            raise RuntimeError(f"Erreur étalonnage: mesure n°{lecturesValides + 1} invalide, {count}/14 octets reçus!")
        else:
            sum_ax += lecture(data[0], data[1]) / 16384.0
            sum_ay += lecture(data[2], data[3]) / 16384.0
            sum_az += lecture(data[4], data[5]) / 16384.0
            
            sum_gx += lecture(data[8], data[9]) / 131.0
            sum_gy += lecture(data[10], data[11]) / 131.0
            sum_gz += lecture(data[12], data[13]) / 131.0

        lecturesValides += 1
        time.sleep(0.01)
        
    offsets = {
    "ax": (sum_ax / lecturesValides) - 1.0,
    "ay": (sum_ay / lecturesValides) - 0.0,
    "az": (sum_az / lecturesValides) - 0.0,

    "gx": (sum_gx / lecturesValides) - 0.0,
    "gy": (sum_gy / lecturesValides) - 0.0,
    "gz": (sum_gz / lecturesValides) - 0.0,
    }

    print(f"[MPU6050] Étalonnage terminé ! Offsets calculés : {offsets}")

    return offsets



#----------------------------------------------------------Max_Distance_Sonar---------------------------------------------------------------------------------


MAX_VALID_DISTANCE = 300

def getValidDistance():
    d = rover.getDistance()
    if d > MAX_VALID_DISTANCE:
        return None  
    return d


# ----------------------------Evitement----------------------------------------------------------------------------------------------------------------

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



#-------------------------------------Fonction pour estimer la vitesse de déplacement du rover:------------------------------------------------------------------
def calculVitesse(speed):
    vMaxTheorique = 10.5
    vSeuil = 26
    
    if abs(speed) < vSeuil:
        return 0.0
    
    puissance = (abs(speed) - vSeuil) / (100 - vSeuil)
    vitesse = puissance * vMaxTheorique

    return round(vitesse, 2)



#--------------------------------------------calcul vitesse rover sur 1m---------------------------------------------------------------------------------
# d1 = rover.getDistance()
# time.sleep(1)
# start = time.time()

# try:
#     offsets = etalonnage(adresse, echantillons=150)
#     goForward(speed)

#     while True:  
        
#         d = rover.getDistance()
#         print(d)
#         if abs(( d1 - d)) >= 50 :
#             print("babaaa")
#             end =time.time()
#             print("temps:",end-start)
#             break
            

#         valeur = mesure(adresse, offsets)

#         print(f"""
# Accéleration (g)    : X = {valeur["ax"]} | Y = {valeur["ay"]} | Z = {valeur["az"]}
# Gyroscope (°/s)     : X = {valeur["gx"]} | Y = {valeur["gy"]} | Z = {valeur["gz"]}""")
        
#         time.sleep(0.02)
       
# finally:
#     rover.cleanup()
#     pi.bb_i2c_close(SDA)
#     pi.stop()

#-------------------------------------------------rotations 90°----------------------------------------------------------------------------------------------



def tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0):
   
    if sens == "droite":
        rover.spinRight(vitesse)
    elif sens == "gauche":
        rover.spinLeft(vitesse)
    else:
        raise ValueError("sens doit être 'droite' ou 'gauche'")
 
    angle_parcouru = 0.0
    dernier_temps = time.time()
    debut = dernier_temps
    compteur = 0

    while abs(angle_parcouru) < angle_cible:
        m = mesure(adresse, offsets, seuilGyro)
        maintenant = time.time()
        dt = maintenant - dernier_temps
        dernier_temps = maintenant
 
        
        angle_parcouru += abs(m["gx"]) * dt


        compteur += 1
        if compteur % 10 == 0:  # affiche 1 fois sur 10 pour ne pas noyer la console
            print(f"gx={m['gx']:7.2f}  gy={m['gy']:7.2f}  gz={m['gz']:7.2f}  "
                  f"dt={dt*1000:5.1f}ms  angle_parcouru={angle_parcouru:6.2f}°")

 
        if maintenant - debut > timeout:
            print("[tourner] Timeout de sécurité atteint pendant le virage")
            break
 
        time.sleep(0.005)
 
    rover.brake()
    print(f"Nombre total de mesures effectuées : {compteur}")


#----------------------------------------------------------demitour----------------------------------------------------------------------------

def demitour_D():
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="droite", vitesse=50, seuilGyro=0.5, timeout=5.0)  


def demitour_G():
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)
    goForward(speed)
    time.sleep(1.5)
    tourner_90(offsets, angle_cible=90, sens="gauche", vitesse=50, seuilGyro=0.5, timeout=5.0)  


# def SonarDistance():

#     d1 = rover.getDistance()
#     time.sleep(1)

#     goForward(speed)

#     while True:  
            
#         d = rover.getDistance()
#         print(d)
#         if abs(( d1 - d)) >= 50 :
#             print("babaaa")

#             break


                
            
MAX_VALID_DISTANCE = 300
MAX_JUMP_CM = 8
SONAR_DELAY = 0.03


def lire_distance_brute():
    d = rover.getDistance()
    if d > MAX_VALID_DISTANCE:
        return None
    return d


def SonarDistance(taille_case=30):
    d1 = None
    while d1 is None:
        d1 = lire_distance_brute()
        time.sleep(SONAR_DELAY)
    goForward(speed)

    derniere_distance_valide = d1

    while True:
        d = lire_distance_brute()
        time.sleep(SONAR_DELAY)

        if d is None:
            continue

        # Rejet des sauts physiquement impossibles (bruit ponctuel isolé)
        if abs(d - derniere_distance_valide) > MAX_JUMP_CM:
            print(f"Mesure rejetée (saut trop important) : {d:.1f} cm")
            continue

        derniere_distance_valide = d
        print(d)

        if abs(d1 - d) >= taille_case:
            rover.brake()
            print("case atteinte")
            break
        
















#------------------------------------------------------Grille_1.50x1----------------------------------------------------------------------------------------

offsets = etalonnage(adresse, echantillons=150)
time.sleep(0.5)

x = 0
y = 0

try:
    while True:
        # Déplacement par pas de 50cm
        SonarDistance()

        # ---- Arrêt pour mesure ----
        rover.brake()
        time.sleep(1)

        # Incrémentation de la position x
        posX += 1
        # Si on a complété la grille, on arrête le programme
        if x==posX and y==posY:
            break

        # Si on est en bout de ligne, le rover fait un demi-tour
        if x==posX:
            demitour_D(speed, offsets)
            y +=1

            # Même principe que précédemment, mais dans l'autre sens
            while posX !=0:
                SonarDistance(speed, rover)

                # ---- Arrêt pour mesure ----
                rover.brake()
                time.sleep(1)

                posX -= 1

            # Une fois la ligne complètée, on fait demi-tour dans l'autre sens
            demitour_G(speed, offsets)
            posY += 1

        # Si on a complété la grille, on arrête le programme
        if x==posX and y==posY:
            break

except KeyboardInterrupt:
    pass

finally: 
    print("\n[main.py] Nettoyage et fermeture...\n")
    rover.cleanup()
    try:
        pi.bb_i2c_close(SDA)
    except:
        pass
    

