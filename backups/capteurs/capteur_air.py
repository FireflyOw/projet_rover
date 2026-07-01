import smbus2, time

adress = 0x50
bus = smbus2.SMBus(1)

def mesure():
    bus.write_byte(adress, 0x88)
    time.sleep(1)
    data = bus.read_i2c_block_data(adress, 0x00, 29)

    pm1_atm = (data[10] << 8) | data[11]
    pm25_atm = (data[12] << 8) | data[13]
    pm10_atm = (data[14] << 8) | data[15]

    return {
        "pm1_atm": pm1_atm,
        "pm25_atm": pm25_atm,
        "pm10_atm": pm10_atm,
    }

while True:
    valeur = mesure()

    print(f"""PM 1 : {valeur["pm1_atm"]} ug/m3
PM2.5 : {valeur["pm25_atm"]} ug/m3
PM10 : {valeur["pm10_atm"]} ug/m3""")
    
    time.sleep(2)