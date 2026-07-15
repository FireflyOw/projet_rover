import os, csv, time, numpy

lastTrigger = 0

# Fonction de mesure avec les capteurs HM3301 (particules) et DHT22 (temp/hum):
def mesures(adresse, capteur, pi, SDA):
    global lastTrigger
    try:
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
            capteur.trigger()

            if time.time() >= lastTrigger + 0.2:
                temperature = capteur.temperature()
                humidite = capteur.humidity()

                temp_hum = {
                "temperature": round(temperature, 1), 
                "humidite": round(humidite, 1), 
                "unite_temp": "°C", 
                "unite_hum": "%",
                }

                lastTrigger = time.time()

        except (RuntimeError, AttributeError):
            pass

        try:
            pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x88, 3, 0])
            lastMesure = time.time()

            if lastMesure < time.time() + 0.3:
                count, data = pi.bb_i2c_zip(SDA, [4, 0x40, 2, 6, 29, 3, 0])

                if count < 29:
                    raise RuntimeError(f"Erreur: lecture incomplète, {count}/29 octets reçus!")

                pm1_atm = (data[10] << 8) | data[11]
                pm25_atm = (data[12] << 8) | data[13]
                pm10_atm = (data[14] << 8) | data[15]

                air = {
                    "pm1_atm": pm1_atm,
                    "pm25_atm": pm25_atm,
                    "pm10_atm": pm10_atm,
                    "unite": "µg/m3"
                }

                lastMesure = time.time()
        except (RuntimeError, OSError, AttributeError):
            pass
        
        if temp_hum["temperature"] == "Erreur!" and air["pm1_atm"] == "Erreur!":
            raise RuntimeError("[HM3301, DHT22] Capteurs indisponibles!")
        elif temp_hum["temperature"] == "Erreur!":
            raise RuntimeError("[DHT22] Capteur indisponible!")
        elif air["pm1_atm"] == "Erreur!":
            raise RuntimeError("[HM3301] Capteur indisponible!")
        
    except RuntimeError as e:
        print(f"[mesures.py]{e}")
        #return fakeMesures()

    return { **temp_hum, **air}
    
# # Fausse fonction pour les essais de mesure sans la Pi Zero ou les capteurs:        
# def fakeMesures():
#     return {
#             "temperature": numpy.random.randint(10, 70), 
#             "humidite": numpy.random.randint(35, 90), 
#             "unite_temp": "°C", 
#             "unite_hum": "%",
#             "pm1_atm": numpy.random.randint(1, 10),
#             "pm25_atm": numpy.random.randint(1, 10),
#             "pm10_atm": numpy.random.randint(1, 10),
#             "unite": "µg/m3",
#         }

# Fonction pour l'écriture des données de mesure dans un fichier csv:
def ecriture(valeurs=None, grid_x=0, grid_y=0):
    os.makedirs(os.path.join(os.path.dirname(__file__), "données"), exist_ok=True)

    CSV_PATH = os.path.join(os.path.dirname(__file__), "données", time.strftime("mesures%b%d.csv"))
    colonnes = ["timestamp", "temp_c", "humidity", "pm1", "pm2_5", "pm10", "grid_x", "grid_y"]
    fichier = os.path.exists(CSV_PATH) 

    try:
        if valeurs["temperature"] == "Erreur!" and valeurs["pm1_atm"] == "Erreur!":
            raise RuntimeError("[HM3301, DHT22] Écriture impossible!")
        elif valeurs["temperature"] == "Erreur!":
            raise RuntimeError("[DHT22] Écriture impossible!")
        elif valeurs["pm1_atm"] == "Erreur!":
            raise RuntimeError("[HM3301] Écriture impossible!")
    
    except (Exception, RuntimeError, TypeError, NameError) as e:
        print(f"[mesures.py]{e}")

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