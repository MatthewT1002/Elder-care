import cv2
import os
import numpy as np

dataset_path = "dataset"

cascade_path = os.path.join(cv2.__path__[0], "data", "haarcascade_frontalface_default.xml")
face_cascade = cv2.CascadeClassifier(cascade_path)
if face_cascade.empty():
    raise RuntimeError("Failed to load Haar cascade xml")

faces = []
labels = []
label_map = {}
current_label = 0

for person_name in os.listdir(dataset_path):
    person_path = os.path.join(dataset_path, person_name)
    if not os.path.isdir(person_path):
        continue

    label_map[current_label] = person_name

    for img_name in os.listdir(person_path):
        img_path = os.path.join(person_path, img_name)
        img = cv2.imread(img_path)
        if img is None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        detected_faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in detected_faces:
            faces.append(gray[y:y+h, x:x+w])
            labels.append(current_label)

    current_label += 1

faces = np.array(faces, dtype=object)
labels = np.array(labels)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, labels)

# Save model
recognizer.write("trainer.yml")
print("[INFO] Training complete, saved to trainer.yml")

# Save label mapping
import json
with open("labels.json", "w") as f:
    json.dump(label_map, f)
print("[INFO] Label mapping saved to labels.json")

