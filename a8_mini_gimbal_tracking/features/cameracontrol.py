
import math
import threading
import queue
import time
class cameraGimbalHandler():
    def __init__(self, ControlSDK):
        self.Gimbal = ControlSDK
        self.ScreenHeight = 0
        self.ScreenWidth = 0
        self.HFOV = 0  
        self.VFOV = 0
        self.MAX_YAW = 0
        self.MIN_YAW = 0
        self.MAX_PITCH = 0
        self.MIN_PITCH = 0
        self.MAX_ZOOM = 6
        self.MIN_ZOOM = 0
        self.CenterX = 0
        self.CenterY = 0
        self.yaw ,self.pitch ,self.roll = 0,0,0
        self.gimbal_queue = queue.Queue()
        self.gimbal_running = True
        self.gimbal_buzzy = False
        self.CurrentZoomLevel = 0
        self.ZoomState =0


    
    def connectGimbal(self):
        if self.Gimbal.connect() :
            return True
        
        return False
    
    def GimbalZoomIN(self):
        self.ZoomState = self.CurrentZoomLevel+1
        if self.MIN_ZOOM <= self.ZoomState <= self.MAX_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.ZoomState)
            self.CurrentZoomLevel = self.ZoomState
        elif self.ZoomState < self.MIN_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.MIN_ZOOM)
            self.CurrentZoomLevel = self.MIN_ZOOM
        elif self.ZoomState < self.MAX_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.MAX_ZOOM)
            self.CurrentZoomLevel = self.MAX_ZOOM

    def GimbalZoomOut(self):
        self.ZoomState = self.CurrentZoomLevel-1
        if self.MIN_ZOOM <= self.ZoomState <= self.MAX_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.ZoomState)
            self.CurrentZoomLevel = self.ZoomState
        elif self.ZoomState < self.MIN_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.MIN_ZOOM)
            self.CurrentZoomLevel = self.MIN_ZOOM
        elif self.ZoomState < self.MAX_ZOOM:
            self.Gimbal.requestAbsoluteZoom(self.MAX_ZOOM)
            self.CurrentZoomLevel = self.MAX_ZOOM





    def intializeGimbal(self):

        if self.connectGimbal():
            self.Gimbal.requestFollowMode()
            self.yaw ,self.pitch ,self.roll = self.Gimbal.getAttitude()
            self.CurrentZoomLevel = self.Gimbal.getCurrentZoomLevel()

            return True
        return False

    def gimbalControl(self):
        while self.gimbal_running:
            try:
                state,yaw, pitch = self.gimbal_queue.get(timeout=0.5)
                self.gimbal_buzzy = True
                if state == "need":
                    self.setMoveSteps(yaw,pitch)
                    self.gimbal_buzzy = False
                    continue
                    
                elif state == "direct":
                    self.Gimbal.setGimbalRotation(yaw,pitch)
                    self.gimbal_buzzy = False
                    self.yaw, self.pitch = yaw,pitch
                    continue
                

                
            except queue.Empty:
                continue

    def startGimbalControl(self):
        self.gimbal_thread = threading.Thread(target=self.gimbalControl, daemon=True)
        self.gimbal_thread.start()

    def setGimbalIp(self,IPAddress_port:tuple):
        self.Gimbal._server_ip,self.Gimbal._port = IPAddress_port

    def setResolution(self, height:int,width:int):
        self.ScreenHeight = height
        self.ScreenWidth = width
        self.CenterX, self.CenterY = self.findCenterPoint(self.ScreenHeight,self.ScreenWidth)

    def gimbalMove(self,method,need_yaw,need_pitch):

        if not self.gimbal_buzzy:
            self.gimbal_queue.put((method,need_yaw,need_pitch))
            

    def setField_of_view(self, HFOV,VFOV):
        self.HFOV = HFOV
        self.VFOV = VFOV

    def setLimts(self, min_yaw:int,max_yaw:int,min_pitch:int,max_pitch:int):
        self.MIN_YAW = min_yaw
        self.MAX_YAW = max_yaw
        self.MIN_PITCH =min_pitch
        self.MAX_PITCH =max_pitch


    def findCenterPoint(self,Frameheight, Framewidth):
        centerX = Framewidth//2
        centerY = Frameheight//2
        return centerX, centerY
    
    def isPossibleMove(self, need_yaw,need_pitch):
        desired_yaw =self.yaw + need_yaw
        desired_pitch = self.pitch + need_pitch
    
        if desired_pitch >= self.MIN_PITCH and desired_pitch <= self.MAX_PITCH and desired_yaw <= self.MAX_YAW and desired_yaw >= self.MIN_YAW:
   
            return True
        
        
        return False
    
    
    def findPitchAndYaw(self,SelectedPoint:tuple):
        cX,cY = self.CenterX,self.CenterY
        selectedX,selectedY = SelectedPoint
        delta_x = selectedX - cX
        delta_y = selectedY - cY

        yaw = -delta_x * (self.HFOV /self.ScreenWidth)
        pitch = -delta_y * (self.VFOV /self.ScreenHeight)
        
        return round(yaw, 1) , round(pitch, 1)
    
    def setMoveSteps(self, need_yaw,need_pitch):
        self.yaw = self.yaw + need_yaw
        self.pitch = self.pitch + need_pitch
        if self.yaw < self.MIN_YAW:
            self.yaw = self.MIN_YAW
        elif self.yaw > self.MAX_YAW:
            self.yaw = self.MAX_YAW
        
        if self.pitch <self.MIN_PITCH:
            self.pitch = self.MIN_PITCH
        elif self.pitch > self.MAX_PITCH:
            self.pitch = self.MAX_PITCH
        self.Gimbal.setGimbalRotation(self.yaw,self.pitch)
   
        

    def centerGimbal(self):
        self.Gimbal.requestCenterGimbal()

    def getShape(self):
        return self.ScreenHeight, self.ScreenWidth
    
    def getCenter(self):
        return self.CenterX, self.CenterY
    
    def destroy(self):
        self.gimbal_running = False
        self.gimbal_thread.join()
        self.Gimbal.disconnect()


        