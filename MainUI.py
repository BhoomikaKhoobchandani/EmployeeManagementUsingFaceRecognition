from PyQt5 import QtWidgets, uic
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
import sys
from datetime import datetime, date
# import pi_face_recognition
import cv2
from imutils.video import VideoStream
import getpics
import encode_faces
import sqlite3
import pandas as pd
#import Camera

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('Admin.ui', self) # Load the .ui file
        self.EmpSave.clicked.connect(self.onClicked)
        self.EmpCapture.clicked.connect(self.onClickedCapture)
        self.EmpTraining.clicked.connect(self.onClickedTraining)
        self.EmpButton.clicked.connect(self.onClickedSearch)
        self.ManualButton.clicked.connect(self.onClickedManual)
        self.EmpDelete.clicked.connect(self.onClickedDelete)
        self.GoBack.clicked.connect(self.onClickedBack)
        self.AttendanceDownload.clicked.connect(self.onClickedAdate)

    def onClickedAdate(self):
        conn = sqlite3.connect('FaceRecognition.db', isolation_level=None,
                           detect_types=sqlite3.PARSE_COLNAMES)
        c = conn.cursor()
        self.date=self.StartDate.text()
        self.Edate=self.EndDate.text()
        dd,mm,yy = [y for x in self.date.split() for y in x.split('-')]
        edd,emm,eyy = [y for x in self.Edate.split() for y in x.split('-')]

        print(dd,mm,yy,edd,emm,eyy) 

        for i in range(int(yy),int(eyy)+1):
            for j in range(int(mm),int(emm)+1):
                for k in range(int(dd),int(edd)+1):
                    check = c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='AOD_{}_{}_{}' '''.format(i,str(j).zfill(2),str(k).zfill(2)))
                    #if the count is 1, then table exists
                    if (check.fetchone()[0]==1):   
                        db_df = pd.read_sql_query("SELECT * from AOD_{}_{}_{}".format(i,str(j).zfill(2),str(k).zfill(2)),conn)
                        db_df.to_csv(('AOD_{}_{}_{}.csv').format(i,str(j).zfill(2),str(k).zfill(2)), index=False)
                print("Done")
        conn.commit()
        conn.close()


    def onClicked(self):
        conn = sqlite3.connect('FaceRecognition.db')
        c = conn.cursor()
        self.name=self.EmpName.text()
        self.Id=self.EmpID.text()
        self.Desig=self.EmpDesig.text()
        self.depart=self.EmpDepart.text()
        self.doj=self.EmpDOJ.text()
        a={}
        key=self.Id
        a.setdefault(key, [])
        a[key].append(self.name)
        a[key].append(self.Desig)
        a[key].append(self.depart)
        a[key].append(self.doj)
        print(a)


        #Storing employee details in employees table
        try:
            c.execute("""INSERT INTO employees(Name, ID, Designation, Department, DateOfJoining) VALUES (?,?,?,?,?)""",(self.name, key, self.Desig, self.depart, self.doj))
            print(a)
            conn.commit()

        except Exception as err:
            print('Query Failed: Error: %s' %(str(err)))    #Pop up Needed 
        
        finally:
            conn.close()

    def onClickedCapture(self):
        getpics.TakeImages(self.Id)

    def onClickedTraining(self):
        encode_faces.TrainImg()

    def onClickedSearch(self):
        conn = sqlite3.connect('FaceRecognition.db')
        c = conn.cursor()
        self.SId=self.EmpSearch.text()
        print(self.SId)
        info = c.execute("""SELECT * FROM employees WHERE ID == {}""".format(self.SId)) 
        info = list(info.fetchone()) 
        print(info)
        self.EmpName.setText(info[0])
        self.EmpID.setText(str(info[1]))
        self.EmpDesig.setText(info[2])
        self.EmpDepart.setText(info[3])
        self.EmpDOJ.setText(info[4])
    
    def onClickedManual(self):
        conn = sqlite3.connect('FaceRecognition.db')
        c = conn.cursor()
        todays_date = str(date.today())
        todays_date = "AOD_" + str(todays_date.replace("-","_"))
        self.MSId=self.ManualSearch.text()
        print(type(self.MSId))
        try:
            # Name to be displayed 
            Name = c.execute("""SELECT Name FROM employees WHERE ID == {}""".format((self.MSId)))
            Name = Name.fetchone()[0]
            # On click OK button
            c.execute(("""INSERT INTO {} (Name, ID, CheckInTime) VALUES (?,?,?)""".format(todays_date)), (str(Name), (self.MSId), datetime.now().strftime("%H:%M:%S")))
            conn.commit()

        except Exception as err:
            # If any error
            print('Query Failed: Error: %s' %(str(err)))    #Pop up Needed 

        finally:
            conn.close()

    def onClickedBack(self):
        self.logC =Camera.Ui()
        self.setCentralWidget(self.logC)
        self.show()

    def onClickedDelete(self):
        self.EmpName.clear()
        self.EmpID.clear()
        self.EmpDesig.clear()
        self.EmpDepart.clear()
        self.EmpDOJ.clear()


if __name__=='__main__':
    conn = sqlite3.connect('FaceRecognition.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS employees 
        (   Name text NOT NULL,
            ID integer PRIMARY KEY,
            Designation text NOT NULL,
            Department text NOT NULL,
            DateOfJoining text NOT NULL
        )""")
    conn.commit()
    conn.close()
    app=QtWidgets.QApplication(sys.argv)
    window=Ui()
    window.show()
    sys.exit(app.exec_())