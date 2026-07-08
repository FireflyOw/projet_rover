import csv, time, numpy

def capt_air(adress, bus):
    try:
        bus.write_byte(adress, 0x88)
        time.sleep(0.3)
        data = bus.read_i2c_block_data(adress, 0x00, 29)

        pm1_atm = (data[10] << 8) | data[11]
        pm25_atm = (data[12] << 8) | data[13]
        pm10_atm = (data[14] << 8) | data[15]

        return {
            "pm1_atm": pm1_atm,
            "pm25_atm": pm25_atm,
            "pm10_atm": pm10_atm,
            "unite": "µg/m3",
        }
    
    except OSError:
        return {
            "pm1_atm": "Erreur!",
            "pm25_atm": "Erreur!",
            "pm10_atm": "Erreur!",
            "unite": "",
        }

def temp_hum(capteur):

    try:
        temperature = capteur.temperature
        humidite = capteur.humidity

        return {
            "temperature": temperature, 
            "humidite": humidite, 
            "unite_temp": "°C", 
            "unite_hum": "%",
        }

    except RuntimeError:
        return {
            "temperature": "Erreur!", 
            "humidite": "Erreur!", 
            "unite_temp": "", 
            "unite_hum": ""
        }
    
def ecriture(adresse):
    valeur_air = capt_air(adresse)
    val_temp_hum = temp_hum()

    with open("mesures.csv", mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow({val_temp_hum["temperature"]},
                        {val_temp_hum["humidite"]}, 
                        {valeur_air['pm1_atm']}, 
                        {valeur_air['pm25_atm']}, 
                        {valeur_air['pm10_atm']})
        
        
# Fausses fonction pour les essais de mesure sans la Pi Zero:        
def fakeTemp():
    temperature = numpy.random.randint(10, 70)
    humidite = numpy.random.randint(35, 90)    

    return {
            "temperature": temperature, 
            "humidite": humidite, 
            "unite_temp": "°C", 
            "unite_hum": "%",
        }

def fakeAir():
    pm1_atm = numpy.random.randint(1, 10)
    pm25_atm = numpy.random.randint(1, 10)
    pm10_atm = numpy.random.randint(1, 10)

    return {
            "pm1_atm": pm1_atm,
            "pm25_atm": pm25_atm,
            "pm10_atm": pm10_atm,
            "unite": "µg/m3",
        }

print(ecriture())