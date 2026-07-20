from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from luma.core.render import canvas

import pigpio, time

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

    def closeI2C(self):
        try:
            pi.bb_i2c_close(SDA)
        except:
            pass

SDA, SCL = 25, 5
adresseAir = 0x40
adresseOLED = 0x3D

print("[main.py] Démarrage écran et bus I2C...")
pi = pigpio.pi()
try:
    pi.bb_i2c_close(SDA)
except pigpio.error:
    pass

# Ouverture du bus I2C:
pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)
print(f"[main.py] Bus I2C ouvert! SDA: {SDA}, SCL: {SCL}")


interfaceI2C = gestionI2C(pi, SDA, address=adresseOLED)
ecran = ssd1306(interfaceI2C, width=128, height=32, rotate=0)

with canvas(ecran) as draw:
    draw.rectangle(ecran.bounding_box, outline="white", fill="black")
    draw.text((5, 10), "DFRobot 0.91\" OK", fill="white")