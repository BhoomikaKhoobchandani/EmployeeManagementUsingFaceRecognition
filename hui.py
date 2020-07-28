# USB camera display using PyQt and OpenCV, from iosoft.blog
# Copyright (c) Jeremy P Bentham 2019
# Please credit iosoft.blog if you use the information or software in it

VERSION = "Cam_display v0.10"

import sys, time, threading, cv2
import MainUI
try:
    from PyQt5.QtCore import Qt
    pyqt5 = True
except:
    pyqt5 = False
if pyqt5:
    from PyQt5.QtCore import QTimer, QPoint, pyqtSignal
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt5.QtWidgets import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QFont, QPainter, QImage, QTextCursor
else:
    from PyQt4.QtCore import Qt, pyqtSignal, QTimer, QPoint
    from PyQt4.QtGui import QApplication, QMainWindow, QTextEdit, QLabel
    from PyQt4.QtGui import QWidget, QAction, QVBoxLayout, QHBoxLayout
    from PyQt4.QtGui import QFont, QPainter, QImage, QTextCursor
try:
    import Queue as Queue
except:
    import queue as Queue
from datetime import date,datetime
import pickle
import os
import face_recognition
import pyttsx3
import sqlite3

IMG_SIZE    = 1280,720          # 640,480 or 1280,720 or 1920,1080
IMG_FORMAT  = QImage.Format_RGB888
DISP_SCALE  = 2                # Scaling factor for display image
DISP_MSEC   = 50                # Delay between display cycles
CAP_API     = cv2.CAP_ANY       # API: CAP_ANY or CAP_DSHOW etc...
EXPOSURE    = 0                 # Zero for automatic exposure
TEXT_FONT   = QFont("Courier", 10)
# emp = 'Unknown'
camera_num  = 1                 # Default camera (first in list)
image_queue = Queue.Queue()     # Queue to hold images
capturing   = True              # Flag to indicate capturing

# Grab images from the camera (separate thread)
class detect():
	# def __init__(self):

	def grab_images(self, cam_num, queue):
	    cap = cv2.VideoCapture(cam_num-1 + CAP_API)
	    cap.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_SIZE[0])
	    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_SIZE[1])
	    print("[INFO] loading encodings + face detector...")
	    file = open('encodings', 'rb')
	    data = pickle.load(file)
	    detector = cv2.CascadeClassifier(os.getcwd()+'\\'+'haarcascade_frontalface_default.xml')
	    print("[INFO] starting video stream...")
	    if EXPOSURE:
	        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
	        cap.set(cv2.CAP_PROP_EXPOSURE, EXPOSURE)
	    else:
	        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
	    while capturing:
	        if cap.grab():
	            retval, image = cap.retrieve(0)
	            if image is not None and queue.qsize() < 2:
	                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	                rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5,minSize=(30, 30),flags=cv2.CASCADE_SCALE_IMAGE)
	                boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]
	                encodings = face_recognition.face_encodings(rgb, boxes)
	                names = []
	                for encoding in encodings:
	                    matches = face_recognition.compare_faces(data["encodings"],encoding)
	                    # global name
	                    self.name = "Unknown"
	                    if True in matches:
	                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
	                        counts = {}
	                        for i in matchedIdxs:
	                            self.name = data["names"][i]
	                            counts[self.name] = counts.get(self.name, 0) + 1
	                        self.name = max(counts, key=counts.get)
	                    names.append(self.name)
	                    queue.put(image)
	                    # Text.setText(name)
	                    # emp = name

	                for ((top, right, bottom, left), self.name) in zip(boxes, names):
	                    cv2.rectangle(image, (left, top), (right, bottom),(0, 255, 0), 2)
	                    y = top - 15 if top - 15 > 15 else top + 15
	                    cv2.putText(image, self.name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,0.75, (0, 255, 0), 2)
	                    #self.Text.setText(name)
	                    if(self.name!="Unknown"):
	                        engine = pyttsx3.init()
	                        engine.say("Good Morning"+ self.name)
	                        engine.runAndWait()
	                        detect.database(self,self.name)
	                        break

	                    else:
	                        engine = pyttsx3.init()
	                        engine.say("Not Recognised please contact Admin")
	                        engine.runAndWait()
	                        break
	                    break
	            else:
	                time.sleep(DISP_MSEC / 1000.0)
	        else:
	            print("Error: can't grab camera image")
	            break

	    cap.release()
	    # return self.name

	def database(self, name):
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
		i=0
		conn2 = sqlite3.connect('FaceRecognition.db', timeout=40.0)
		c2 = conn2.cursor()
		print(name)
		if name!="Unknown":
		    try:
		        Name = c2.execute("""SELECT Name FROM employees WHERE ID == {}""".format(name))
		        Name = Name.fetchone()[0]
		        if i==0:
		            c2.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (str(Name), name, datetime.now().strftime("%H:%M:%S")))
		            conn2.commit()
		            i=1

		        conn2.commit()

		    except Exception as err:
		        print('Query Failed: Error: %s' %(str(err)))
		        # break    #Pop up Needed
		        # c1.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (emp, '-', datetime.now().strftime("%H:%M:%S")))

		    finally:
		        c2.close()
		        conn2.close()
		else:
		    conn1 = sqlite3.connect('FaceRecognition.db', timeout=40.0)
		    c1 = conn1.cursor()
		    c1.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), ('Unknown', ' ', datetime.now().strftime("%H:%M:%S")))
		    c1.close()
		    conn1.close()
        


# Image widget
class ImageWidget(QWidget):
    def __init__(self, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        self.setMinimumSize(image.size())
        self.update()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QPoint(0, 0), self.image)
        qp.end()

# Main window
class MyWindow(QMainWindow):
    text_update = pyqtSignal(str)

    # Create main window
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.central = QWidget(self)
        self.textbox = QTextEdit(self.central)
        self.textbox.setFont(TEXT_FONT)
        self.textbox.setMinimumSize(300, 100)
        # self.text_update.connect(self.append_text)
        sys.stdout = self
        print("Camera number %u" % camera_num)
        print("Image size %u x %u" % IMG_SIZE)
        if DISP_SCALE > 1:
            print("Display scale %u:1" % DISP_SCALE)

        self.vlayout = QVBoxLayout()        # Window layout
        self.displays = QHBoxLayout()
        self.disp = ImageWidget(self)    
        self.displays.addWidget(self.disp)
        self.vlayout.addLayout(self.displays)
        self.label = QLabel(self)
        self.vlayout.addWidget(self.label)
        self.vlayout.addWidget(self.textbox)
        self.central.setLayout(self.vlayout)
        self.setCentralWidget(self.central)

        self.mainMenu = self.menuBar()      # Menu bar
        AdminAction = QAction('&Admin', self)
        startAction=QAction('&Start',self)
        self.lbb=MainUI.Ui()
        AdminAction.triggered.connect(self.process)
        startAction.triggered.connect(self.start)
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.AdminMenu = self.mainMenu.addMenu('&Admin')
        self.ExitMenu = self.mainMenu.addMenu('&Exit')
        self.StartMenu=self.mainMenu.addMenu('&Start')
        self.AdminMenu.addAction(AdminAction)
        self.ExitMenu.addAction(exitAction)
        self.StartMenu.addAction(startAction)

    def process(self):
    	self.lbb =MainUI.Ui()
    	self.setCentralWidget(self.lbb)
    	self.show()

    # Start image capture & display
    def start(self):
        self.timer = QTimer(self)           # Timer to trigger display
        self.timer.timeout.connect(lambda: 
                    self.show_image(image_queue, self.disp, DISP_SCALE))
        self.timer.start(DISP_MSEC)    
           
        # name = detect.grab_images(self, camera_num, image_queue)  
        self.capture_thread = threading.Thread(target=detect.grab_images, 
                    args=(self, camera_num, image_queue))
        self.capture_thread.start()         # Thread to grab images
        # self.store_thread = threading.Thread(target=detect.database, args=(name))
        # self.store_thread.start()

    # Fetch camera image from queue, and display it
    def show_image(self, imageq, display, scale):
        if not imageq.empty():
            image = imageq.get()
            if image is not None and len(image) > 0:
                img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.display_image(img, display, scale)

    # Display an image, reduce size if required
    def display_image(self, img, display, scale=1):
        disp_size = img.shape[1]//scale, img.shape[0]//scale
        disp_bpl = disp_size[0] * 3
        if scale > 1:
            img = cv2.resize(img, disp_size, 
                             interpolation=cv2.INTER_CUBIC)
        qimg = QImage(img.data, disp_size[0], disp_size[1], 
                      disp_bpl, IMG_FORMAT)
        display.setImage(qimg)

    # Handle sys.stdout.write: update text display
    def write(self, text):
        self.text_update.emit(str(text))
    def flush(self):
        pass

    # Append to text display
    # def append_text(self, text):
    #     cur = self.textbox.textCursor()     # Move cursor to end of text
    #     cur.movePosition(QTextCursor.End) 
    #     s = str(text)
    #     while s:
    #         head,sep,s = s.partition("\n")  # Split line at LF
    #         cur.insertText(head)            # Insert text at cursor
    #         if sep:                         # New line if LF
    #             cur.insertBlock()
    #     self.textbox.setTextCursor(cur)     # Update visible cursor

    # Window is closing: stop video capture
    def closeEvent(self, event):
        global capturing
        capturing = False
        self.capture_thread.join()
        # self.store_thread.join()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        try:
            camera_num = int(sys.argv[1])
        except:
            camera_num = 0
    if camera_num < 1:
        print("Invalid camera number '%s'" % sys.argv[1])
    else:
        # global emp
        app = QApplication(sys.argv)
        win = MyWindow()
        win.show()
        win.setWindowTitle(VERSION)
        # win.start()
        # win.store()
        sys.exit(app.exec_())