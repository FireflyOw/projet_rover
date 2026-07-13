import time, pigpio, config.DHT22 as DHT22

pi = pigpio.pi()
capteur = DHT22.sensor(pi, 25)

while True:
    try:
        capteur.trigger()
        time.sleep(0.2)
        temperature = capteur.temperature
        humidite = capteur.humidity

        if temperature == -999:
            raise RuntimeError("Lecture invalide!")

        print(f"Température : {temperature:.1f}°C")
        print(f"Humidité : {humidite:.1f}%")

    except RuntimeError as e:
        print(f"Erreur de lecture {e}")