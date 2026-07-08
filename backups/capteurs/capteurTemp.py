import time, adafruit_dht, board

erreur = ""
timeout = 5
nbMesures = 0

capteur = adafruit_dht.DHT22(board.D25, use_pulseio=False)

try:
    while True:
        if nbMesures >= timeout:
            print(f"Erreur: {erreur}")
            break

        try:
            temperature = capteur.temperature
            humidite = capteur.humidity

            if temperature != None and humidite != None:
                print(f"Température : {temperature:.1f}°C")
                print(f"Humidité : {humidite:.1f}%")
            else:
                print("""Erreur: lecture impossible!
                      Nouvelle tentative...""")

        except RuntimeError as e:
            erreur = e
            nbMesures += 1
            print(".", end="", flush=True)

        time.sleep(3)

finally:
    capteur.exit()