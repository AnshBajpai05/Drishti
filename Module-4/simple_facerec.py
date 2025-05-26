import cv2
import os
import numpy as np

data_dir = "Module-4/faces"
trainer_path = "Module-4/trainer.yml"
labels_path = "Module-4/labels.txt"

def train_faces(data_dir="Module-4/faces"):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    faces = []
    labels = []
    label_map = {}
    current_id = 0

    for root, dirs, files in os.walk(data_dir):
        print(dirs)
        print(files)
        for file in files:
            if file.endswith("jpg") or file.endswith("png"):
                path = os.path.join(root, file)
                label = os.path.basename(root)
                if label not in label_map:
                    label_map[label] = current_id
                    current_id += 1
                id_ = label_map[label]

                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"[WARNING] Could not load image: {path}")
                    continue

                face_rects = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
                print(f"[DEBUG] Found {len(face_rects)} faces in {path}")

                if img is None:
                    continue
                face_rects = face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
                for (x, y, w, h) in face_rects:
                    faces.append(img[y:y+h, x:x+w])
                    labels.append(id_)
    
    recognizer.train(faces, np.array(labels))
    recognizer.save("Module-4/trainer.yml")

    # Save label map
    with open("Module-4/labels.txt", "w") as f:
        for label, idx in label_map.items():
            f.write(f"{idx},{label}\n")
    print("[INFO] Training complete.")


def load_labels(path="Module-4/labels.txt"):
    labels = {}
    with open(path, "r") as f:
        for line in f:
            idx, name = line.strip().split(",")
            labels[int(idx)] = name
    return labels

def recognise(frame):
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('Module-4/trainer.yml')
    labels = load_labels()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        roi = gray[y:y+h, x:x+w]
        id_, confidence = recognizer.predict(roi)

        if 100 <confidence < 120:
            name = labels.get(id_, "Unknown")
            return name
        else:
            return "Unknown"
    return "NoFace"



train_faces()