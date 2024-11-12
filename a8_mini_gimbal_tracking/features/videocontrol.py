import cv2
import numpy as np
import threading
import time

class videoHandler():
    """
        Camera Video Display 
        User annotations
        Tracking and Detection
    """
    def __init__(self):
        self.rtspUrl = ""
        self.Camera = None
        self.Running = False
        self.StreamingFlag =False
        self.x_clicked =0
        self.y_clicked = 0
        self.VIEWCONTROLLER = False
        self.TargetLocked = False
        self.OSD =False
        self.SELECTED_FLAG = False
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
        self.old_gray = None
        self.PreviousROI = None
        self.notSignal =cv2.imread("assets/signalNotFound.png") 
        if self.notSignal is None:
            self.notSignal =cv2.imread("assets/signalNotFound.png") 
        self.frame = cv2.imread("assets/signalNotFound.png") 

        # self.intializeStreaming()
        
        self.lk_params = dict(winSize = (15,15), maxLevel=2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03))

    

    def selectedCoord(self,x,y):
        self.x_clicked , self.y_clicked =x,y
        self.PreviousROI = np.array([[x,y]], dtype=np.float32)
        self.SELECTED_FLAG = True

    def getSelectedCoord(self):
        return self.x_clicked ,self.y_clicked

    def generatePipline(self, Url="rtsp://192.168.6.121:8554/main.264"):

        if Url.__class__ is int:
            return Url
        
        return f'rtspsrc location={Url} latency=0 ! decodebin ! videoconvert ! appsink'
    
    def setStreammingUrl(self, url:str):
        self.rtspUrl = url


    def intializeStreaming(self):
        if self.rtspUrl =="":
            print("Provide Streaming Url")
            self.frame =  self.notSignal.read()
            self.ImageHeight, self.ImageWidth, _ = self.frame.shape
            self.StreamingFlag =False
        else:
            self.Camera = cv2.VideoCapture(self.generatePipline(self.rtspUrl),cv2.CAP_GSTREAMER )
            time.sleep(2.0)
            if self.Camera.isOpened():
                self.StreamingFlag =True
                self.Running = True
                ret, self.frame =self.Camera.read()
                self.ImageHeight, self.ImageWidth,_ = self.frame.shape
                self.CenterX = self.ImageWidth//2
                self.CenterY = self.ImageHeight//2
            else:
                self.Camera.release()
                self.frame =  self.notSignal
                self.ImageHeight, self.ImageWidth, _ = self.frame.shape
                self.StreamingFlag =False
                
            return True

    def startStreaming(self):
        self.thread = threading.Thread(target=self.StreamingLoop, args=())
        self.thread.daemon = True 
        self.thread.start()

    def getFrame(self):
        return True ,self.frame
    
    def setTargetCenterCoords(self,centerPoint:tuple):
        self.Target_x,self.Target_y  = centerPoint
        
    def getTargetCenterCoords(self):
        return self.Target_x, self.Target_y
    
    def isTargetLocked(self):
        return self.TargetLocked
    
    def StreamingLoop(self):
        while self.Running:
            if not self.StreamingFlag:
                self.frame = self.notSignal
            else:
                ret, self.frame  = self.Camera.read()
                self.draw_plus_point(self.frame,(self.CenterX,self.CenterY),7,(0,255,0),2)
                if self.SELECTED_FLAG:
                    isDetected, centerPoint, rectCoords =self.TrackerHandler(self.frame,"lucas kanade", previousGrayFrame=self.old_gray,previousROI=self.PreviousROI,lk_params=self.lk_params)

                    if isDetected: 
                        self.TargetLocked = True
                        pt1, pt2 = rectCoords   
                        self.draw_plus_point(self.frame,centerPoint,5,(0,0,255),1)
                        self.draw_resizable_focus_rect(self.frame,pt1,pt2,(0,0,255),2)
                        self.setTargetCenterCoords(centerPoint)
                else:
                    self.setTargetCenterCoords((None,None))
                        
    def isClicked(self):
        return self.SELECTED_FLAG
  
    def resetTracker(self):
        self.TargetLocked = False
        self.SELECTED_FLAG = False
        self.old_gray = None
        self.PreviousROI = None


 
    def getShape(self):
        return self.ImageHeight, self.ImageWidth
    
    def displayOSD(self,frame,Data):
        cv2.putText(frame,f"Model Altitude:00 m",(10,20), self.font,0.5,(255,0,255),2) 
    
    def toggleOSD(self,Command:bool):
        self.OSD = Command
        


    def lucas_kanade_tracker(self,frame, previousGrayFrame,previousROI,lk_params):


        frame_gray =  cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        if self.old_gray is not None:
            PresentROI, st,err = cv2.calcOpticalFlowPyrLK(previousGrayFrame,frame_gray,previousROI,None,**lk_params)
            if st[0] == 1:
                x, y  = PresentROI.ravel()
                self.PreviousROI = PresentROI
                x1, y1 = int(x-30), int(y-30)
                x2, y2 = int(x + 30), int(y + 30)
                self.old_gray = frame_gray.copy()

                return True , (x,y) ,((x1,y1),(x2,y2))
        self.old_gray = frame_gray.copy()
        return False,(),()


    def TrackerHandler(self,frame, Tracker_Name, **kwargs):

        match(Tracker_Name):
            case "lucas kanade":
                return self.lucas_kanade_tracker(frame,kwargs["previousGrayFrame"],kwargs["previousROI"],kwargs["lk_params"])
            
            
                
    def destroy(self):
        self.Running = False
        self.TargetLocked = False
        self.thread.join()
        self.Camera.release()

    def draw_plus_point(self,frame,points,arm_length,color,thickness):
        cenX,cenY = points

        cv2.line(frame, (int(cenX), int(cenY - arm_length)), (int(cenX), int(cenY + arm_length)), color, thickness)
        cv2.line(frame, (int(cenX - arm_length),int(cenY)), (int(cenX + arm_length), int(cenY)), color, thickness)

    def draw_resizable_focus_rect(self,frame, pt1, pt2, color=(0, 255, 0), thickness=2, scale_factor=0.1):

        # Unpack points
        x1, y1 = pt1
        x2, y2 = pt2

        # Calculate width and height
        w = x2 - x1
        h = y2 - y1

        # Calculate corner lengths based on the size of the bounding box
        corner_length_w = int(w * scale_factor)  # Corner length proportional to width
        corner_length_h = int(h * scale_factor)  # Corner length proportional to height

        # Ensure corner length doesn't exceed half of the rectangle size
        corner_length_w = min(corner_length_w, w // 2)
        corner_length_h = min(corner_length_h, h // 2)
        
        # Top-left corner
        cv2.line(frame, (x1, y1), (x1 + corner_length_w, y1), color, thickness)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_length_h), color, thickness)

        # Top-right corner
        cv2.line(frame, (x2, y1), (x2 - corner_length_w, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_length_h), color, thickness)

        # Bottom-left corner
        cv2.line(frame, (x1, y2), (x1, y2 - corner_length_h), color, thickness)
        cv2.line(frame, (x1, y2), (x1 + corner_length_w, y2), color, thickness)

        # Bottom-right corner
        cv2.line(frame, (x2, y2), (x2 - corner_length_w, y2), color, thickness)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_length_h), color, thickness)


            
            
        
    




    
        


    



