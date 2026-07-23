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

def mesure(adresse, offsets, seuilGyro = 0.2):
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

def etalonnage(adresse, echantillons = 100):
    print(f"[MPU6050] Étalonnage en cours... Ne pas bouger le rover ({echantillons} mesures)")

    sum_ax, sum_ay, sum_az = 0, 0, 0
    sum_gx, sum_gy, sum_gz = 0, 0, 0
    lecturesValides = 0
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur étalonnage: lecture incomplète, {count}/14 octets reçus!")
    else:
        while lecturesValides < echantillons:
            sum_ax += lecture(data[0], data[1]) / 16384.0
            sum_ay += lecture(data[2], data[3]) / 16384.0
            sum_az += lecture(data[4], data[5]) / 16384.0
            
            sum_gx += lecture(data[8], data[9]) / 131.0
            sum_gy += lecture(data[10], data[11]) / 131.0
            sum_gz += lecture(data[12], data[13]) / 131.0

            lecturesValides += 1
            time.sleep(0.1)
        
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

try:
    offsets = etalonnage(adresse, echantillons=150)

    while True:
        valeur = mesure(adresse, offsets)

        print(f"""
Accéleration (g)    : X = {valeur["ax"]} | Y = {valeur["ay"]} | Z = {valeur["az"]}
Gyroscope (°/s)     : X = {valeur["gx"]} | Y = {valeur["gy"]} | Z = {valeur["gz"]}""")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nTest arrêté proprement.")

finally:
    pi.bb_i2c_close(SDA)
    pi.stop()