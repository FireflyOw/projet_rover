import os, csv, time, psutil

lastTrigger = 0
lastMesure = 0

# Fonction de mesure avec les capteurs HM3301 (particules) et DHT22 (temp/hum):
def mesures(adresse, capteur, pi, SDA):
    global lastTrigger, lastMesure
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

            if time.time() >= lastMesure + 0.3:
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

# Fonction pour l'écriture des données de mesure dans un fichier csv:
def ecriture(valeurs=None, grid_x=0, grid_y=0):
    os.makedirs(os.path.join(os.path.dirname(__file__), "données"), exist_ok=True)

    CSV_PATH = os.path.join(os.path.dirname(__file__), "données", time.strftime("mesures%b%d.csv"))
    colonnes = ["timestamp", 
                "temp_c", "humidity", 
                "pm1", "pm2_5", "pm10", 
                "grid_x", "grid_y"
                "cpu", "cpuTemp", "ramUsed, ramTotale", "ramPercent"
                ]
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
            "grid_y": grid_y,
            "cpu": valeurs['cpu'], 
            "cpuTemp": valeurs['cpuTemp'], 
            "ramUsed": valeurs['ramUsed'], 
            "ramTotale": valeurs['ramTotale'], 
            "ramPercent": valeurs['ramPercent'],
        }) 

    return "[mesures.py] Mesures enregistrées!"

def infosPi():
    ram = psutil.virtual_memory()
    ramUsed = ram.used // 1024 ** 2
    ramTotale = ram.total // 1024 ** 2
    ramPercent = ram.percent

    cpu = psutil.cpu_percent(interval=1)
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        cpuTemp = int(f.read()) / 1000
    
    return {"cpu": cpu, 
            "cpuTemp": cpuTemp, 
            "ramUsed": ramUsed, 
            "ramTotale": ramTotale, 
            "ramPercent": ramPercent,
            }