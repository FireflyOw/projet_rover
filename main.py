import sys, os, time, adafruit_dht, board, smbus2
from mouvements import goForward, evitement, speed
from mesures import mesures, ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[main.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[main.py] fakeRover.py chargé (PC)")

# Paramètres capteurs:
adresse = 0x40
bus = smbus2.SMBus(1)
try:
    capteur = adafruit_dht.DHT22(board.D25)
except AttributeError:
    capteur = None
    print("[main.py][DHT22] Capteur indisponible!")

# Paramètres mesure:
lastMesure = 0
intervalMesure = 1
distance = []

# Paramètres rover:
avancer = False
spin = False

# ---- Boucle principale : ----
rover.init(0)

# Main:
run = True
try:
    while run:
        # --Bloc mesures--
        
        distance.append(rover.getDistance())
        if len(distance) >= 5000:
            distance.pop(0)

        if time.time() >= lastMesure + intervalMesure:
            valeurs = mesures(adresse, capteur, bus)
            ecriture(adresse, capteur, bus)
            
            print(f"Temp: {valeurs['temperature']} {valeurs['unite_temp']} | Hum: {valeurs['humidite']} {valeurs['unite_hum']}")
            print(f"Distance: {int(distance[-1])}cm")
            lastMesure = time.time()

        # --Bloc déplacements--

        if avancer == False:
            goForward(speed)
            avancer = True            
            spin = False

        if all(x<=30 for x in distance[-5:]):
            while all(int(distance[-1])-1 < x and x <  int(distance[-1])+1 for x in distance[-50:]):
                distance.append(rover.getDistance())
                time.sleep(0.001)
                print(distance[-1:])
                
                if spin == False:
                    rover.spinLeft(speed)
                    spin = True
                    avancer = False
                print("bloblo")

        time.sleep(0.001)

finally: 
    rover.cleanup()