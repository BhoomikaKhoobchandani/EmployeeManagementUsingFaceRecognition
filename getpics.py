import cv2
import os
# from gtts import gTTS 
def createFolder(directory):
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                return directory
        except OSError: 
            print("false")
            print ('Error: Creating directory. ' +  directory)
            return False
def TakeImages(name):
    face_cascade = cv2.CascadeClassifier(os.getcwd()+'\\'+'haarcascade_frontalface_default.xml')
    video = cv2.VideoCapture(0) 
    count=0
    folder_name = os.getcwd()+"\\"+"faces"+"\\"+name
    path=createFolder(folder_name)
    while True:
        global gray
        count+=1
        check, frame = video.read()
        cv2.imshow("Capturing",frame) 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame, 1.5, 5)
        for (x, y, w, h) in faces:
            roi_gray=gray[y:y+h,x:x+w]
            cv2.rectangle(frame, (x,y), (x+w,y+h), (255,0,0), 2)
            dst = 6421 / w
            dst = '%.2f' %dst
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, str(dst), (x, y-10), font, 1, (0, 50, 250), 1, cv2.LINE_AA)
            print(dst)
            if(float(dst)>20.00 or float(dst)<50.00):
                cv2.imwrite(os.path.join(folder_name,"Image"+str(count)+".jpg"),roi_gray)
            else:
                pass
        cv2.imshow("Capturing",frame)
        key = cv2.waitKey(1)
        if count == 50:
            break
    video.release()
    cv2.destroyAllWindows
