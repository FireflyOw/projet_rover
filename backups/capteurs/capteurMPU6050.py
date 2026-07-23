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

def mesure(adresse, offsets):
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur mesure: lecture incomplète, {count}/14 octets reçus!")
    else:
        ax = round(lecture(data[0], data[1]) / 16384.0, 2) - offsets["ax"]
        ay = round(lecture(data[2], data[3]) / 16384.0, 2) - offsets["ay"]
        az = round(lecture(data[4], data[5]) / 16384.0, 2) - offsets["az"]
        
        gx = round(lecture(data[8], data[9]) / 131.0, 1)   - offsets["gx"]
        gy = round(lecture(data[10], data[11]) / 131.0, 1) - offsets["gy"]
        gz = round(lecture(data[12], data[13]) / 131.0, 1) - offsets["gz"]

    return {
        "ax": ax,
        "ay": ay,
        "az": az,

        "gx": gx,
        "gy": gy,
        "gz": gz,
    }

def etalonnage(adresse, echantillons = 100):
    print(f"[MPU6050] Étalonnage en cours... Ne pas bouger le rover ({echantillons} mesures)")

    sum_ax, sum_ay, sum_az = 0, 0, 0
    sum_gx, sum_gy, sum_gz = 0, 0, 0
    lecturesValides = 0
    count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

    if count < 14:
        raise RuntimeError(f"Erreur étalonnage: lecture incomplète, {count}/14 octets reçus!")
    else:
        sum_ax += round(lecture(data[0], data[1]) / 16384.0, 2)
        sum_ay += round(lecture(data[2], data[3]) / 16384.0, 2)
        sum_az += round(lecture(data[4], data[5]) / 16384.0, 2)
        
        sum_gx += round(lecture(data[8], data[9]) / 131.0, 1)
        sum_gy += round(lecture(data[10], data[11]) / 131.0, 1)
        sum_gz += round(lecture(data[12], data[13]) / 131.0, 1)

        lecturesValides += 1
        time.sleep(0.1)
        
    offsets = {
    "ax": round((sum_ax / lecturesValides) - 1.0, 2),
    "ay": round((sum_ay / lecturesValides) - 0.0, 2),
    "az": round((sum_az / lecturesValides) - 0.0, 2),

    "gx": round((sum_gx / lecturesValides) - 0.0, 2),
    "gy": round((sum_gy / lecturesValides) - 0.0, 2),
    "gz": round((sum_gz / lecturesValides) - 0.0, 2),
    }

    print(f"[MPU6050] Étalonnage terminé ! Offsets calculés : {offsets}")

    return offsets

try:
    offsets = etalonnage(adresse, echantillons=150)

    while True:
        valeur = mesure(adresse, offsets)

        print(f"""
Accéleration (g)    : X = {valeur["ax"] + offsets["ax"]} | Y = {valeur["ay"] + offsets["ay"]} | Z = {valeur["az"] + offsets["az"]}
Gyroscope (°/s)     : X = {valeur["gx"] + offsets["gx"]} | Y = {valeur["gy"] + offsets["gy"]} | Z = {valeur["gz"] + offsets["gz"]}""")

        time.sleep(0.2)

except KeyboardInterrupt:
    print("\nTest arrêté proprement.")

finally:
    pi.bb_i2c_close(SDA)
    pi.stop()