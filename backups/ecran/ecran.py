import pigpio
import time
from luma.oled.device import ssd1306
from luma.core.render import canvas

class gestionI2C:
    def __init__(self, pi_instance, sda_pin, address=0x3C):
        self.pi = pi_instance
        self.sda = sda_pin
        self.address = address
    
    def command(self, *cmd):
        payload = [0x00] + list(cmd)
        chain = [4, self.address, 2, 7, len(payload)] + payload + [3, 0]
        self.pi.bb_i2c_zip(self.sda, chain)

    def data(self, data):
        chunk_size = 64
        for i in range(0, len(data), chunk_size):
            chunk = list(data[i:i+chunk_size])
            payload = [0x40] + chunk
            chain = [4, self.address, 2, 7, len(payload)] + payload + [3, 0]
            self.pi.bb_i2c_zip(self.sda, chain)

    def cleanup(self):
        # Méthode requise par Luma lors de la fermeture
        pass

SDA, SCL = 25, 5
adresseOLED = 0x3C 

print("[main.py] Démarrage écran et bus I2C...")
pi = pigpio.pi()

try:
    pi.bb_i2c_close(SDA)
except pigpio.error:
    pass

# Ouverture du bus I2C logiciel à 100 kHz
pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)
print(f"[main.py] Bus I2C ouvert! SDA: {SDA}, SCL: {SCL}")

posX = 2
posY = 4

try:
    interfaceI2C = gestionI2C(pi, SDA, address=adresseOLED)
    ecran = ssd1306(interfaceI2C, width=128, height=32, rotate=0)

    with canvas(ecran) as draw:
        draw.text((25, 0), "Deplacement ...", fill="white")
        draw.text((0, 15), f"X={posX} ; Y={posY} | CPU=32% RAM=21%", fill="white")
        

    print("[main.py] Affichage envoyé! CTRL + C pour arrêter...")

    # Indispensable pour maintenir le bus ouvert pendant le test
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    pass

finally:
    pi.bb_i2c_close(SDA)
    with canvas(ecran) as draw:
        pass