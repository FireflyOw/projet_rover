import time

def init(brightness=40):
    print("[rover] init()")

def cleanup():
    print("[rover] cleanup()")

def forward(speed):
    print(f"[rover] forward({speed})")

def reverse(speed):
    print(f"[rover] reverse({speed})")

def stop():
    print("[rover] stop()")

def brake():
    print("[rover] brake()")

def spinLeft(speed):
    print(f"[rover] spinLeft({speed})")

def spinRight(speed):
    print(f"[rover] spinRight({speed})")

def setServo(servo, degrees):
    print(f"[rover] setServo({servo}, {degrees})")

def getDistance():
    return 50.0