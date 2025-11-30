import time
import cv2
import socket
import struct

host_ip = 'IP_ADDRESS' #Ip address of remote server
host_socket = 0000 #Socket of server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host_ip, host_socket))

face_cas = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Camera not accessed")
    exit()

print("Camera is active!")

