import time, sys, os,  pigpio

dossier = os.path.dirname(__file__)
racineProjet = os.path.abspath(os.path.join(dossier, "..", ".."))
sys.path.append(racineProjet)

import config.DHT22 as DHT22

pi = pigpio.pi()
capteur = DHT22.sensor(pi, 24)

while True:
    try:
        capteur.trigger()
        time.sleep(0.2)
        temperature = capteur.temperature()
        humidite = capteur.humidity()

        if temperature == -999:
            raise RuntimeError("Lecture invalide!")

        print(f"Température : {round(temperature, 1)}°C")
        print(f"Humidité : {humidite}%")

    except RuntimeError as e:
        print(f"Erreur de lecture {e}")

    time.sleep(1)