import sys
import numpy as np
from imutils.video import VideoStream
import cv2
from PyQt5 import QtCore,uic
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore  import pyqtSlot
from PyQt5.QtGui import QImage , QPixmap
from PyQt5.QtWidgets import QDialog , QApplication
from PyQt5.uic import loadUi
from imutils.video import FPS
import face_recognition
import argparse
import imutils
import pickle
import time
import cv2
import os
import sqlite3
from datetime import datetime, date
import pyttsx3
# import MainUI

class Ui(QtWidgets.QMainWindow):
	def __init__(self):
		super(Ui,self).__init__()
		#loadUi("student3.ui",self)
		uic.loadUi("Second.ui",self)
		
		self.logic = 0
		self.value = 1
		self.Start.clicked.connect(self.onClicked)
		# self.Admin.clicked.connect(self.onClickedAdmin)
		# self.Exit.clicked.connect(self.onClickedBack)
		#self.TEXT.setText("Kindly Press 'Show' to connect with webcam.")
		#self.CAPTURE.clicked.connect(self.CaptureClicked)

	@pyqtSlot()
	def onClicked(self):
		todays_date = str(date.today())
		todays_date = "AOD_" + str(todays_date.replace("-","_"))
		# PRAGMA foreign_keys=ON
		conn = sqlite3.connect('FaceRecognition.db')
		c = conn.cursor()
		crete_query = ("""CREATE TABLE IF NOT EXISTS {} 
	        (   Name text NOT NULL,
	            ID text PRIMARY KEY,
	            CheckInTime text NOT NULL,
	            CONSTRAINT fk
	            FOREIGN KEY (ID)
	            REFERENCES employees(ID)
	        )""".format(str(todays_date))) 
		c.execute(crete_query)
		conn.commit()
		conn.close()

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

			conn2 = sqlite3.connect('FaceRecognition.db', timeout=40.0)
			c2 = conn2.cursor()

			if emp!="Unknown":
				try:
					Name = c2.execute("""SELECT Name FROM employees WHERE ID == {}""".format(emp))
					Name = Name.fetchone()[0]
					if i==0:
						c2.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (str(Name), emp, datetime.now().strftime("%H:%M:%S")))
						conn2.commit()
						i=1
						break
					conn2.commit()

				except Exception as err:
					print('Query Failed: Error: %s' %(str(err)))
					break    #Pop up Needed
					# c1.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (emp, '-', datetime.now().strftime("%H:%M:%S")))

				finally:
					c2.close()
					conn2.close()
			else:
				conn1 = sqlite3.connect('FaceRecognition.db', timeout=40.0)
				c1 = conn1.cursor()
				c1.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), ('Unknown', '-', datetime.now().strftime("%H:%M:%S")))
				c1.close()
				conn1.close()
				break

			# conn2 = sqlite3.connect('FaceRecognition.db', timeout=40.0)
			# c2 = conn2.cursor()
			# if i==0:
			# 	c2.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (str(Name), emp, datetime.now().strftime("%H:%M:%S")))
			# 	conn2.commit()
			# 	i=1
			# 	break

			# c2.close()
			# conn2.close()

			self.displayImage(frame,1)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		cap.close()
		window.close()
		cv2.destroyAllWindows()
		cap.stop()
		# self.cap.release()
  #   
	def displayImage(self,img,window=1):
		qformat=QImage.Format_Indexed8
		if len(img.shape)==3:
			if(img.shape[2])==4:
				qformat=QImage.Format_RGBA888
			else:
				qformat=QImage.Format_RGB888
		img = QImage(img,img.shape[1],img.shape[0],qformat)
		img = img.rgbSwapped()
		self.Camera.setPixmap(QPixmap.fromImage(img))
		self.Camera.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

	# def onClickedAdmin(self):
	# 	self.lbb =MainUI.Ui()
	# 	self.setCentralWidget(self.lbb)
	# 	self.show()

	# def onClickedBack(self):
	# 		#window.close
	# 		#app.exec_()
	# 		sys.exit()
	# 		self.Text.setText("")
		#self.setCentralWidget(self.log2)
app =  QApplication(sys.argv)
window=Ui()
window.show()
try:
	sys.exit(app.exec_())
except:
	print('exitng')
