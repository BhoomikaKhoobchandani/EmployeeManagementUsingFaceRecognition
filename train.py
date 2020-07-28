import os
import cv2
import face_recognition
import numpy as np
from tqdm import tqdm
from collections import defaultdict
import pickle
import shutil


def takeImg():
    face_cascPath = 'haarcascade_frontalface_alt.xml'
    dataset = 'faces'

    face_detector = cv2.CascadeClassifier(face_cascPath)

    print("[LOG] Collecting images ...")
    images = []
    for direc, _, files in tqdm(os.walk(dataset)):
        for file in files:
            if file.endswith("jpg") or file.endswith("jpeg") or file.endswith("png"):
                images.append(os.path.join(direc,file)) 
    return (face_detector, images)

def process_and_encode(images):
    # initialize the list of known encodings and known names
    known_encodings = []
    known_names = []
    print("[LOG] Encoding faces ...")

    for image_path in tqdm(images):
        # Load image
        image = cv2.imread(image_path)
        # Convert it from BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
     
        # detect face in the image and get its location (square boxes coordinates)
        boxes = face_recognition.face_locations(image, model='hog')

        # Encode the face into a 128-d embeddings vector
        encoding = face_recognition.face_encodings(image, boxes)

        # the person's name is the name of the folder where the image comes from
        name = image_path.split(os.path.sep)[-2]

        if len(encoding) > 0 : 
            known_encodings.append(encoding[0])
            known_names.append(name)

    return {"encodings": known_encodings, "names": known_names}

def main():
    (face_detector, images) = takeImg()
    data = process_and_encode(images)
    print(data) 
    file = open('train_data', 'wb')
    pickle.dump(data, file)
    file.close()
    # src=os.getcwd()+"\\"+"faces"+"\\"
    # dst=os.getcwd()+"\\"+"Trained"+"\\"
    # for f in os.listdir(src):
    #     print(f)
    #     src_file=os.path.join(src,f)
    #     dst_file=os.path.join(dst,f)
    #     shutil.move(src_file,dst_file)
    return(data, face_detector, images)

# if __name__ == "__main__":
