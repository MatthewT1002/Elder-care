import RPi.GPIO as GPIO
import time

# BCM numbering
GPIO.setmode(GPIO.BCM)

# GPIO pin connected to relay
RELAY_PIN = 17  # BCM 17 = physical pin 11
GPIO.setup(RELAY_PIN, GPIO.OUT)

print("Relay test: will turn ON for 2s, then OFF")

GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn ON
time.sleep(2)
GPIO.output(RELAY_PIN, GPIO.LOW)   # Turn OFF

print("Blink 3 times")
for _ in range(3):
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(RELAY_PIN, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()
print("Test complete")
