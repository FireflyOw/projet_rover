import time, pigpio

SDA, SCL = 25, 5
adresse = 0x40

pi = pigpio.pi()
pi.bb_i2c_open(SDA, SCL, 100000)
time.sleep(0.3)

def mesure():
    pi.bb_i2c_zip(SDA, [4, 0x40, 2, 7, 1, 0x88, 3, 0])
    time.sleep(0.3)

    count, data = pi.bb_i2c_zip(SDA, [4, 0x40, 2, 6, 29, 3, 0])

    if count < 29:
        raise RuntimeError(f"Erreur: lecture incomplète, {count}/29 octets reçus!")

    pm1_atm = (data[10] << 8) | data[11]
    pm25_atm = (data[12] << 8) | data[13]
    pm10_atm = (data[14] << 8) | data[15]

    return {
        "pm1_atm": pm1_atm,
        "pm25_atm": pm25_atm,
        "pm10_atm": pm10_atm,
    }

try:
    while True:
        valeur = mesure()

        print(f"""PM 1 : {valeur["pm1_atm"]} ug/m3
PM2.5 : {valeur["pm25_atm"]} ug/m3
PM10 : {valeur["pm10_atm"]} ug/m3""")
        
        time.sleep(2)

finally:
    pi.bb_i2c_close(SDA)