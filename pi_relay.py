import time
import os
from gpiozero import OutputDevice

RELAY_PIN = 17
OPEN_TIME = 3       # seconds door stays unlocked
COOLDOWN = 5        # seconds between unlocks
SIGNAL_FILE = "/tmp/unlock_door"

relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

last_open = 0

print("Door controller running")

while True:
    if os.path.exists(SIGNAL_FILE):
        now = time.time()

        if now - last_open > COOLDOWN:
            print("Unlock signal received")
            relay.on()
            time.sleep(OPEN_TIME)
            relay.off()
            last_open = now

        os.remove(SIGNAL_FILE)

    time.sleep(0.1)
