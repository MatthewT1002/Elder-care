import time
import socket
import struct
from gpiozero import OutputDevice
from gpiozero.pins.rpigpio import RPiGPIOFactory
from gpiozero import Device

import cv2
import numpy as np

Device.pin_factory = RPiGPIOFactory()  
RELAY_PIN = 17 #GPIO pin used
OPEN_TIME = 3 #Seconds door unlocked
COOLDOWN = 5 #Seconds between unlocks

relay = OutputDevice(RELAY_PIN, active_high=True, initial_value=False)
last_open = 0

SERVER_IP = "192.168.1.207" #Server IP
SERVER_PORT = 42069 #Server port (May need changed depending on network)

ALLOWED_USERS = ["Matthew_T"] #User that door will unlock for
CONFIDENCE_THRESHOLD = 60  #Change if needed

cam = cv2.VideoCapture(0) #Camera Setup stuff
if not cam.isOpened():
    print("Cannot access")
    exit()

print("Camera active!")


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Server Script
try:
    sock.connect((SERVER_IP, SERVER_PORT))
    print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")
except Exception as e:
    print("Cannot connect to server:", e)
    cam.release()
    exit()

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

        face_count_bytes = sock.recv(4) #Receive number of faces
        if not face_count_bytes:
            continue

        face_count = struct.unpack(">I", face_count_bytes)[0]

        for _ in range(face_count):  #Receive recognition results
            result_bytes = sock.recv(24)
            if not result_bytes:
                continue

            x, y, w, h, label, confidence = struct.unpack(">6I", result_bytes)
            label_map = {0: "Harry", 1: "Matthew_R", 2: "Matthew_T", 3: "Arpitha"}  # Must match trainer.yml
            name = label_map.get(label, "Unknown")
            #TODO: Could pull list automatically from .yml file if time

            cv2.putText( #Draw Lable for testing stuff
                frame,
                f"{name} ({confidence})",
                (x, max(20, y-10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            if name in ALLOWED_USERS and confidence <= CONFIDENCE_THRESHOLD: #Relay Logic
                now = time.time()
                if now - last_open > COOLDOWN:
                    print(f"Unlocking for {name} (confidence {confidence})")
                    relay.on()
                    time.sleep(OPEN_TIME)
                    relay.off()
                    last_open = now

        cv2.imshow("Camera Feed", frame) #Show camera (Not needed if using web UI TODO: Web UI intergration)
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