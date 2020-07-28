from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import Image1
import time
import image2
import MainUI
import sys
import sqlite3
from datetime import datetime, date
import hui
#import Camera

class TimerWindow(QMainWindow):
	def __init__(self, *args, **kwargs):
		super(TimerWindow, self).__init__(*args, **kwargs)
		self.counter = 0
		layout = QVBoxLayout()
		self.l = QLabel("Starting application...")
		b = QPushButton("Buffering..!")
		b.pressed.connect(self.oh_no)
		layout.addWidget(self.l)
		layout.addWidget(b)
		w = QWidget()
		w.setLayout(layout)
		self.setCentralWidget(w)
		self.show()
		self.timer = QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.recurring_timer)
		self.timer.start()
		# todays_date = str(date.today())
		# todays_date = "AOD_" + str(todays_date.replace("-","_"))
		# # PRAGMA foreign_keys=ON
		# conn = sqlite3.connect('FaceRecognition.db')
		# c = conn.cursor()
		# crete_query = ("""CREATE TABLE IF NOT EXISTS {} 
	 #        (   Name text NOT NULL,
	 #            ID text PRIMARY KEY,
	 #            CheckInTime text NOT NULL,
	 #            CONSTRAINT fk
	 #            FOREIGN KEY (ID)
	 #            REFERENCES employees(ID)
	 #        )""".format(str(todays_date))) 
		# c.execute(crete_query)
		# conn.commit()
		# conn.close()
	def oh_no(self):
		time.sleep(5)

	def recurring_timer(self):
		self.counter +=1
		if(self.counter==5):
			self.log =Image1.MainWindow()
			self.setCentralWidget(self.log)
			self.show()
		if(self.counter==10):
			self.logo =image2.MyLabelPixmap()
			self.setCentralWidget(self.logo)
			self.show()
		if(self.counter==15):
			self.log2 =hui.MyWindow()
			self.setCentralWidget(self.log2)
			VERSION ="Cam_display v0.10"
			self.log2.setWindowTitle(VERSION)
			#self.log2.start()

			self.show()
		#self.l.setText("Counter: %d" % self.counter)
    
def main():  
	app = QApplication([])
	window = TimerWindow()
	sys.exit(app.exec_())
	

main()