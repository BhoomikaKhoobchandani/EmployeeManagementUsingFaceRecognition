import sys
import numpy as np
from imutils.video import VideoStream
import cv2
from imutils.video import FPS
import face_recognition
import threading 
from code import grab_images
grab_images()
print(image_queue)
class detect_face:
	def __init__(self):
		threading.Thread.__init__(self)

	def detect(self):
		print("[INFO] loading encodings + face detector...")
		file = open('encodings', 'rb')
		data = pickle.load(file)
		detector = cv2.CascadeClassifier(os.getcwd()+'\\'+'haarcascade_frontalface_default.xml')
		print("[INFO] starting video stream...")
		cap =VideoStream(src=0).start()
		fps = FPS().start()
		while(True):
			frame = cap.read()
			gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
			rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
			boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
			encodings = face_recognition.face_encodings(rgb, boxes)
			names = []
			for encoding in encodings:
				matches = face_recognition.compare_faces(data["encodings"],encoding)
				name = "Unknown"
				if True in matches:
					matchedIdxs = [i for (i, b) in enumerate(matches) if b]
					counts = {}
					for i in matchedIdxs:
						name = data["names"][i]
						counts[name] = counts.get(name, 0) + 1
					name = max(counts, key=counts.get)
				names.append(name)
				self.Text.setText(name)
				global emp
				emp = name
			i=0	
			for ((top, right, bottom, left), name) in zip(boxes, names):
				cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 0), 2)
				y = top - 15 if top - 15 > 15 else top + 15
				cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
				#self.Text.setText(name)
				if(name!="Unknown"):
					engine = pyttsx3.init()
					engine.say("Good Morning")
					engine.runAndWait()
					break

				else:
					engine = pyttsx3.init()
					engine.say("Not Recognised please contact Admin")
					engine.runAndWait()
					break
				break
