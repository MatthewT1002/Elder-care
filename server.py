import socket
import struct
import cv2
import numpy as np

HOST = "10.104.9.104"   # Listen on all network interfaces
PORT = 42069        # Match your Pi script

# ------------------------------
# Setup Server
# ------------------------------
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"[INFO] Waiting for Pi connection on port {PORT}...")
conn, addr = server.accept()
print(f"[INFO] Connected by {addr}")

# ------------------------------
# Receive Loop
# ------------------------------
try:
    while True:
        # Read 4-byte length
        header = conn.recv(4)
        if not header:
            break  # Pi disconnected

        frame_len = struct.unpack(">I", header)[0]

        # Read the actual frame bytes
        data = b""
        while len(data) < frame_len:
            packet = conn.recv(frame_len - len(data))
            if not packet:
                break
            data += packet

        # Decode JPEG → OpenCV image
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)

        if img is None:
            continue

        cv2.imshow("Pi Camera Feed", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    conn.close()
    server.close()
    cv2.destroyAllWindows()
    print("[INFO] Server closed.")
