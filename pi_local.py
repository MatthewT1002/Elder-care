import time
import socket
import struct
from gpiozero import OutputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import Device

import cv2
import numpy as np

Device.pin_factory = RPiGPIOFactory()
RELAY_PIN = 17
OPEN_TIME = 3
COOLDOWN = 5

relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)
last_open = 0

SERVER_IP = "172.22.250.112"
SERVER_PORT = 42069

ALLOWED_USERS = ["Matthew_T"]
CONFIDENCE_THRESHOLD = 60  # Must match server

cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("Cannot access camera")
    exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
except Exception as e:
    print("Cannot connect to server:", e)
    cam.release()
    exit()

label_map = {0: "Harry", 1: "Matthew_R", 2: "Matthew_T", 3: "Arpitha"} # Change when trainer is run

try:
    while True:
        ret, frame = cam.read()
        if not ret:
            continue

        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            continue

        data = buffer.tobytes()
        sock.sendall(struct.pack(">I", len(data)))
        sock.sendall(data)

        face_count_bytes = sock.recv(4)
        if not face_count_bytes:
            continue
        face_count = struct.unpack(">I", face_count_bytes)[0]

        for _ in range(face_count):
            result_bytes = sock.recv(24)
            if not result_bytes:
                continue

            x, y, w, h, label, confidence = struct.unpack(">4I2i", result_bytes)

            # Unknown face check
            if label == -1:
                name = "UNKNOWN"
            else:
                name = label_map.get(label, "UNKNOWN")

            cv2.putText(
                frame,
                f"{name} ({confidence})",
                (x, max(20, y-10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # Unlock logic
            if label != -1 and name in ALLOWED_USERS and confidence <= CONFIDENCE_THRESHOLD:
                now = time.time()
                if now - last_open > COOLDOWN:
                    print(f"Unlocking for {name} (confidence {confidence})")
                    relay.on()
                    time.sleep(OPEN_TIME)
                    relay.off()
                    last_open = now

        cv2.imshow("Camera Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopped")

finally:
    cam.release()
    sock.close()
    relay.off()
    cv2.destroyAllWindows()
    print("Client exited cleanly")
