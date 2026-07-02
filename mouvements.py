import sys, os, time
#from mesures import ecriture

sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "capteurs"))
sys.path.append(os.path.join(os.path.dirname(__file__), "backups", "rover"))

try:
    import rover
    print("[mouvement.py] rover.py chargé (Raspberry Pi Zero)")
except RuntimeError:
    import fakeRover as rover
    print("[mouvements.py] fakeRover.py chargé (PC)")


# Paramètres capteurs :
adress_captAir = 0x40