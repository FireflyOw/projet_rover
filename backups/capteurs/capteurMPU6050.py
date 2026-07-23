import time, pigpio

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

def mesure(adresse):
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur: lecture incomplète, {count}/14 octets reçus!")
    else:
        ax = round(lecture(data[0], data[1]) / 16384.0, 2)
        ay = round(lecture(data[2], data[3]) / 16384.0, 2)
        az = round(lecture(data[4], data[5]) / 16384.0, 2)
        
        gx = round(lecture(data[8], data[9]) / 131.0, 1)
        gy = round(lecture(data[10], data[11]) / 131.0, 1)
        gz = round(lecture(data[12], data[13]) / 131.0, 1)

    return {
        "ax": ax,
        "ay": ay,
        "az": az,

        "gx": gx,
        "gy": gy,
        "gz": gz,
    }

try:
    while True:
        valeur = mesure(adresse)

        print(f"""
Accéleration (g)    : X = {valeur["ax"]:} | Y = {valeur["ay"]:} | Z = {valeur["az"]:}
Gyroscope (°/s)     : X = {valeur["gx"]:} | Y = {valeur["gy"]:} | Z = {valeur["gz"]:}""")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nTest arrêté proprement.")

finally:
    pi.bb_i2c_close(SDA)
    pi.stop()