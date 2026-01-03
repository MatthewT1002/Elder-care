import time
import cv2
import socket
import struct

HOST_IP = "192.168.1.207"   # Server IP
HOST_PORT = 42069         # Server port

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST_IP, HOST_PORT))

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not accessed")
    exit()

print("Camera is active!")

try:
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed frame grab")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Draw local detection boxes
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            continue

        data = buffer.tobytes()
        data_len = len(data)

        sock.sendall(struct.pack(">I", data_len))
        sock.sendall(data)

        face_count_bytes = sock.recv(4)
        if not face_count_bytes:
            continue

        face_count = struct.unpack(">I", face_count_bytes)[0]

        for _ in range(face_count):
            result_bytes = sock.recv(24)
            if not result_bytes:
                continue

            x, y, w, h, label, confidence = struct.unpack(">6I", result_bytes)

            # Label mapping (must match server)
            if label == 0:
                name = "Matthew_T"
            elif label == 1:
                name = "Matthew_R"
            elif label == 2:
                name = "Harry"
            elif label == 3:
                name = "Arpitha"                
            else:
                name = "Unknown"

            cv2.putText(
                frame,
                f"{name} ({confidence})",
                (x, max(20, y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        cv2.imshow("Local Camera", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopped manually")

finally:
    cam.release()
    sock.close()
    cv2.destroyAllWindows()
    print("All interfaces clear.")
