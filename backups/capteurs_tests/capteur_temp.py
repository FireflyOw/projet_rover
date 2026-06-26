import time, adafruit_dht, adafruit_blinka, board

capteur = adafruit_dht.DHT22(board.D12)

try:
    temperature = capteur.temperature
    humidite = capteur.humidity

    print(f"Température : {temperature:.1f}°C")
    print(f"Humidité : {humidite:.1f}%")

except RuntimeError as e:
    print(f"Erreur de lecture {e}")
finally:
    capteur.exit()