import cv2
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



cap = cv2.VideoCapture(0)
#cap.set(3,1280)
#cap.set(4,720)

detector = htm.handDetector(detectionCon=0.8)


devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()


minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volbar=600
volConv=0



while True:
    #1. preprocess screen
    success, image = cap.read()
    image = cv2.resize(image,(1280,720))
    

    #2. find hand landmarks

    image = detector.findHands(image)
    lmlist = detector.findPosition(image)


    #print(lmlist)

    if len(lmlist)!=0:

        #print(lmlist[4],lmlist[8])


        x1,y1 = lmlist[4][1], lmlist[4][2]
        x2,y2 = lmlist[8][1], lmlist[8][2]
        cx,cy = (x1+x2)//2,(y1+y2)//2
                    
        cv2.circle(image,(x1,y1), 15,(0,255,0),cv2.FILLED)
        cv2.circle(image,(x2,y2), 15,(0,255,0),cv2.FILLED)
        cv2.line(image,(x1,y1),(x2,y2),(255,0,255),3)
        cv2.circle(image,(cx,cy), 15,(0,255,0),cv2.FILLED)
                                               
    #3. length calulation

        length = math.hypot(x2-x1,y2-y1)
        #print(length)  

        if length<35:
            cv2.circle(image,(cx,cy), 15,(0,255,255),cv2.FILLED)

        if length>290:
            cv2.circle(image,(cx,cy), 15,(0,0,255),cv2.FILLED)

    #4. setting volume level

        vol = np.interp(length,(35,290),(minVol,maxVol))
        volConv =np.interp(vol,(minVol,maxVol),(0,100))
        volbar = np.interp(length,(35,290),(600,100))

        #print(length,'---->',vol)


        volume.SetMasterVolumeLevel(vol, None)

        if volConv==100:
            cv2.putText(image,'Max Volume',(650,70),cv2.FONT_HERSHEY_COMPLEX,2,(0,0,255),5)

        elif volConv==0:
            cv2.putText(image,'Min Volume',(650,70),cv2.FONT_HERSHEY_COMPLEX,2,(0,255,0),5)

            


    cv2.rectangle(image,(1100,100),(1200,600),(0,255,0),3)
    cv2.rectangle(image,(1100,int(volbar)),(1200,600),(0,255,0),cv2.FILLED)
    cv2.putText(image,'VoL',(1100,620),cv2.FONT_HERSHEY_COMPLEX_SMALL,2,(0,0,255),5)
    cv2.putText(image,str(int(volConv)),(1100,100),cv2.FONT_HERSHEY_COMPLEX,3,(0,0,0),5)
    cv2.putText(image,'Gesture Volume Control',(0,50),cv2.FONT_HERSHEY_COMPLEX_SMALL,2,(0,255,255),5)
    

                                                
    cv2.imshow('virtual brightness control',image)
    if cv2.waitKey(1) & 0xFF == 27:
        break


