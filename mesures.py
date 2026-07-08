import os, csv, time, numpy

# Fonction de mesure avec les capteurs HM3301 (particules) et DHT22 (temp/hum):
def mesures(adresse, capteur, bus):
    temp_hum = {
            "temperature": "Erreur!", 
            "humidite": "Erreur!", 
            "unite_temp": "", 
            "unite_hum": "",
        }    
    air = {
            "pm1_atm": "Erreur!",
            "pm25_atm": "Erreur!",
            "pm10_atm": "Erreur!",
            "unite": "",
        }
    
    try:
        temperature = capteur.temperature
        humidite = capteur.humidity   

        temp_hum = {
            "temperature": temperature, 
            "humidite": humidite, 
            "unite_temp": "°C", 
            "unite_hum": "%",
        }            
    except (RuntimeError, AttributeError):
        pass

    try:
        bus.write_byte(adresse, 0x88)
        time.sleep(0.3)
        data = bus.read_i2c_block_data(adresse, 0x00, 29)

        pm1_atm = (data[10] << 8) | data[11]
        pm25_atm = (data[12] << 8) | data[13]
        pm10_atm = (data[14] << 8) | data[15]

        air = {
            "pm1_atm": pm1_atm,
            "pm25_atm": pm25_atm,
            "pm10_atm": pm10_atm,
            "unite": "µg/m3",
        }
    except (OSError, AttributeError):
        pass

    return { **temp_hum, **air}
    
# Fausse fonction pour les essais de mesure sans la Pi Zero ou les capteurs:        
def fakeMesures():
    return {
            "temperature": numpy.random.randint(10, 70), 
            "humidite": numpy.random.randint(35, 90), 
            "unite_temp": "°C", 
            "unite_hum": "%",
            "pm1_atm": numpy.random.randint(1, 10),
            "pm25_atm": numpy.random.randint(1, 10),
            "pm10_atm": numpy.random.randint(1, 10),
            "unite": "µg/m3",
        }

def ecriture(adressee=None, capteur=None, bus=None):
    try:
        valeurs = mesures()

        if valeurs["temperature"] == "Erreur!" and valeurs["pm1"] == "Erreur!":
            raise RuntimeError("[HM3301, DHT22] Capteurs indisponibles!")
        elif valeurs["temperature"] == "Erreur!":
            raise RuntimeError("[DHT22] Capteur indisponible!")
        elif valeurs["pm1"] == "Erreur!":
            raise RuntimeError("[HM3301] Capteur indisponible!")
    
    except (Exception, RuntimeError, TypeError, NameError) as e:
        print(f"[mesures.py] Simulation de mesures forcée: {e}")

        valeurs = fakeMesures()

    colonnes = ["temperature", "humidite", "pm1", "pm2.5", "pm10"]
    fichier = os.path.exists("mesures.csv")    

    with open("mesures.csv", mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        if not fichier:
            writer.writeheader()

        writer.writerow({"temperature": valeurs["temperature"],
                        "humidite": valeurs["humidite"], 
                        "pm1": valeurs['pm1_atm'], 
                        "pm2.5": valeurs['pm25_atm'], 
                        "pm10": valeurs['pm10_atm']})
        
    return "Mesures enregistrées!"