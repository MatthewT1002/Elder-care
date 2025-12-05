import time
import cv2
import socket
import struct

host_ip = '10.104.9.104' #Ip address of remote server
host_socket = 42069 #Socket of server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host_ip, host_socket))

#face_cas = cv2.CascadeClassifier(
 #   cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
#)

# Source - https://stackoverflow.com/a
# Posted by alecxe
# Retrieved 2025-12-04, License - CC BY-SA 4.0

face_cas = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not accessed")
    exit()

print("Camera is active!")

try:
    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed Frame Grab")
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cas.detectMultiScale(gray, 1.3, 5)

        for(x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        encode_success, buffer = cv2.imencode('.jpg', frame)
        if not encode_success:
            continue

        data = buffer.tobytes()
        data_len = len(data)

        s.sendall(struct.pack('>I', data_len))
        s.sendall(data)

        cv2.imshow("Local Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.02)

except KeyboardInterrupt:
    print("Stopped manually")

finally:
    cam.release()
    s.close
    cv2.destroyAllWindows()
    print("All interfaces clear.")
    