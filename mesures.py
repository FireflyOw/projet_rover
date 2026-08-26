import os, csv, time, psutil

# Fonction de mesure avec les capteurs HM3301 (particules) et DHT22 (temp/hum):
def mesures(adresse, capteur, pi, SDA):
    try:
        temp_hum = {
                "temperature": "Erreur!", 
                "humidite": "Erreur!",
                "uniteTemp": "",
                "uniteHum": "",
            }    
        air = {
                "pm1_atm": "Erreur!",
                "pm25_atm": "Erreur!",
                "pm10_atm": "Erreur!",
                "uniteAir": "",
            }
        
        try:
            capteur.trigger()
            time.sleep(0.3)

            temperature = capteur.temperature()
            humidite = capteur.humidity()

            temp_hum = {
            "temperature": f"{round(temperature, 1)}°C", 
            "humidite": f"{round(humidite, 1)}%",
            "uniteTemp": "°C",
            "uniteHum": "%",
            }

        except (RuntimeError, AttributeError):
            pass

        try:
            pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x88, 3, 0])
            count, data = pi.bb_i2c_zip(SDA, [4, 0x40, 2, 6, 29, 3, 0])
            time.sleep(0.3)

            if count < 29:
                raise RuntimeError(f"Erreur: lecture incomplète, {count}/29 octets reçus!")

            pm1_atm = (data[10] << 8) | data[11]
            pm25_atm = (data[12] << 8) | data[13]
            pm10_atm = (data[14] << 8) | data[15]

            air = {
                "pm1_atm": f"{pm1_atm}",
                "pm25_atm": f"{pm25_atm}",
                "pm10_atm": f"{pm10_atm}",
                "uniteAir": "µg/m3",
            }

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

# Fonction pour récupérer les infos d'utilisation CPU/RAM de la Pi Zero:
def infosPi():
    ram = psutil.virtual_memory()
    ramUsed = ram.used // 1024 ** 2
    ramTotale = ram.total // 1024 ** 2
    ramPercent = ram.percent

    cpu = psutil.cpu_percent(interval=1)
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        cpuTemp = int(f.read()) / 1000
    
    return {"cpu": cpu, 
            "cpuTemp": f"{cpuTemp:.1f}", 
            "ramUsed": ramUsed, 
            "ramTotale": ramTotale, 
            "ramPercent": ramPercent,
            }

# Fonction pour l'écriture des données de mesure dans un fichier csv:
def ecriture(valeurs=None, grid_x=0, grid_y=0):
    os.makedirs(os.path.join(os.path.dirname(__file__), "données"), exist_ok=True)

    CSV_PATH = os.path.join(os.path.dirname(__file__), "données", time.strftime("mesures%b%d.csv"))
    colonnes = ["timestamp", 
                "temp_c", "humidity", 
                "pm1", "pm2_5", "pm10", 
                "grid_x", "grid_y",
                "cpu", "cpuTemp", "ramUsed", "ramTotale", "ramPercent",
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
            "cpu": valeurs['cpu'], 
            "cpuTemp": valeurs['cpuTemp'], 
            "ramUsed": valeurs['ramUsed'], 
            "ramTotale": valeurs['ramTotale'], 
            "ramPercent": valeurs['ramPercent'],
            "grid_x": grid_x,
            "grid_y": grid_y,
        }) 

    return "[mesures.py][capteurThread] Mesures enregistrées!"

def lecture(h, l):
    valeur = (h << 8) | l
    return valeur - 65536 if valeur >= 0x8000 else valeur

def gyroscope(adresse, pi, SDA, offsets, seuilGyro = 0.2):
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

def etalonnage(adresse, pi, SDA, echantillons = 100):
    print(f"[MPU6050] Étalonnage en cours... Ne pas bouger le rover ({echantillons} mesures)")

    sum_ax, sum_ay, sum_az = 0, 0, 0
    sum_gx, sum_gy, sum_gz = 0, 0, 0
    lecturesValides = 0

    while lecturesValides < echantillons:
        count, data = pi.bb_i2c_zip(SDA, [4, adresse, 2, 7, 1, 0x3B, 2, 6, 14, 3, 0])

        if count < 14:
            raise RuntimeError(f"Erreur étalonnage: mesure n°{lecturesValides + 1} invalide, {count}/14 octets reçus!")
        else:
            sum_ax += lecture(data[0], data[1]) / 16384.0
            sum_ay += lecture(data[2], data[3]) / 16384.0
            sum_az += lecture(data[4], data[5]) / 16384.0
            
            sum_gx += lecture(data[8], data[9]) / 131.0
            sum_gy += lecture(data[10], data[11]) / 131.0
            sum_gz += lecture(data[12], data[13]) / 131.0

        lecturesValides += 1
        time.sleep(0.01)
        
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