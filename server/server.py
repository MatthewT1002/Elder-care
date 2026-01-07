import socket
import struct
import cv2
import numpy as np
import threading
from flask import Flask, Response
import time

HOST = "192.168.20.78"
PORT = 42069

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

recogniser = cv2.face.LBPHFaceRecognizer_create()
recogniser.read("trainer.yml")

label_map = {0: "Harry", 1: "Matthew_R", 2: "Matthew_T", 3: "Arpitha"}
CONFIDENCE_THRESHOLD = 60  # Match client threshold

output_frame = None
frame_lock = threading.lock()

app = Flask(__name__)

def generate_frames():
    global output_frame
    while True:
        with frame_lock:
            if output_frame is None:
                continue
            ret, buffer = cv2.imencode(".jpg", output_frame)
        if not ret:
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            buffer.tobytes() +
            b"\r\n"
        )
        time.sleep(0.03)

@app.route("/video_feed")
def video_feed():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

def start_flask():
    app.run(host="0.0.0.0", port=5000, threaded=True)

threading.Thread(target=start_flask, daemon=True).start()
print("MJPEG stream running at http://172.22.250.112:5000/video_feed")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Server listening...")
conn, addr = server.accept()
print("Connected:", addr)

try:
    while True:
        # Receive frame size header
        header = conn.recv(4)
        if not header:
            break
        frame_len = struct.unpack(">I", header)[0]

        # Receive frame data
        data = b""
        while len(data) < frame_len:
            packet = conn.recv(frame_len - len(data))
            if not packet:
                break
            data += packet

        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        response = []

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            label, confidence = recogniser.predict(face)

            # Unknown face handling
            if confidence > CONFIDENCE_THRESHOLD:
                label = -1

            confidence = int(min(max(confidence, -2**31), 2**31-1))

            response.append((x, y, w, h, label, confidence))

        with frame_lock:
            output_frame = frame.copy()

        # Send number of faces
        try:
            conn.sendall(struct.pack(">I", len(response)))
            # Send each face info
            for item in response:
                x, y, w, h, label, confidence = item
                conn.sendall(struct.pack(">4I2i", x, y, w, h, label, confidence))
        except BrokenPipeError:
            print("[WARN] Client disconnected.")
            break

except KeyboardInterrupt:
    print("Server stopped")

finally:
    conn.close()
    server.close()
    print("Server closed")

    print("Server closed")
