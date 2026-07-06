import time, adafruit_dht, board

capteur = adafruit_dht.DHT22(board.D25, use_pulseio=False)
try:
    while True:
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
            print(f"Erreur de lecture {e}")
        
        time.sleep(2)

finally:
    capteur.exit()