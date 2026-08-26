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