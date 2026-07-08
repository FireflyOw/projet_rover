import time

def init(brightness=40):
    print("[rover.py] init()")

def cleanup():
    print("[rover.py] cleanup()")

def forward(speed):
    print(f"[rover.py] forward({speed})")

def reverse(speed):
    print(f"[rover.py] reverse({speed})")

def stop():
    print("[rover.py] stop()")

def brake():
    print("[rover.py] brake()")

def spinLeft(speed):
    print(f"[rover.py] spinLeft({speed})")

def spinRight(speed):
    print(f"[rover.py] spinRight({speed})")

def setServo(servo, degrees):
    print(f"[rover.py] setServo({servo}, {degrees})")

def getDistance():
    return 50.0