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

# Fonction pour l'écriture des données de mesure dans un fichier csv:
def ecriture(adresse=None, capteur=None, bus=None, grid_x=0, grid_y=0):
    os.makedirs(os.path.join(os.path.dirname(__file__), "données"), exist_ok=True)

    CSV_PATH = os.path.join(os.path.dirname(__file__), "données", time.strftime("mesures%b%d.csv"))
    colonnes = ["timestamp", "temp_c", "humidity", "pm1", "pm2_5", "pm10", "grid_x", "grid_y"]
    fichier = os.path.exists(CSV_PATH) 

    try:
        valeurs = mesures(adresse, capteur, bus)

        if valeurs["temperature"] == "Erreur!" and valeurs["pm1_atm"] == "Erreur!":
            raise RuntimeError("[mesures.py][HM3301, DHT22] Capteurs indisponibles!")
        elif valeurs["temperature"] == "Erreur!":
            raise RuntimeError("[mesures.py][DHT22] Capteur indisponible!")
        elif valeurs["pm1_atm"] == "Erreur!":
            raise RuntimeError("[mesures.py][HM3301] Capteur indisponible!")
    
    except (Exception, RuntimeError, TypeError, NameError) as e:
        print(f"[mesures.py] Simulation: {e}")

        valeurs = fakeMesures()   

    with open(CSV_PATH, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=colonnes)
        if not fichier:
            writer.writeheader()

        writer.writerow({"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "temp_c": valeurs["temperature"],
                        "humidity": valeurs["humidite"], 
                        "pm1": valeurs['pm1_atm'], 
                        "pm2_5": valeurs['pm25_atm'], 
                        "pm10": valeurs['pm10_atm'],
                        "grid_x": grid_x,
                        "grid_y": grid_y
        })
        
    return "[mesures.py] Mesures enregistrées!"