import socket
import struct
import cv2
import numpy as np

HOST = "192.168.1.207" #Server IP
PORT = 42069 #Server Port

face_cas = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

recogniser = cv2.face.LBPHFaceRecognizer_create()
recogniser.read("trainer.yml")

label_map = {
    0: "Matthew_T",
    1: "Matthew_R",
    2: "Harry",
    3: "Arpitha"
}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Server listening...")
conn, addr = server.accept()
print("Connected:", addr)

try:
    while True:
        header = conn.recv(4)
        if not header:
            break

        frame_len = struct.unpack(">I", header)[0]

        data = b""
        while len(data) < frame_len:
            packet = conn.recv(frame_len - len(data))
            if not packet:
                break
            data += packet

        frame = cv2.imdecode(
            np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR
        )
        if frame is None:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cas.detectMultiScale(gray, 1.3, 5)

        response = []

        for (x, y, w, h) in faces:
            face = gray[y:y+h, x:x+w]
            face = cv2.resize(face, (200, 200))

            label, confidence = recogniser.predict(face)
            name = label_map.get(label, "Unknown")

            response.append((x, y, w, h, label, int(confidence)))

        # Send back number of faces
        conn.sendall(struct.pack(">I", len(response)))

        for item in response:
            conn.sendall(struct.pack(">6I", *item))

except KeyboardInterrupt:
    print("Server stopped")

finally:
    conn.close()
    server.close()
    print("Server closed")
