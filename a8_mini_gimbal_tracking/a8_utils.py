
"""
Modifed by Joel T George 
For handling camera controll and setup the gimbal limits
"""
import math
class Camera:
    def __init__(self, ControlSDK):
        self.Gimbal =ControlSDK
        self.ScreenHeight = 0
        self.ScreenWidth = 0
        self.HFOV = 0  
        self.VFOV = 0
        self.MAX_YAW = 0
        self.MIN_YAW = 0
        self.MAX_PITCH = 0
        self.MIN_PITCH = 0
        self.CenterX = 0
        self.CenterY = 0
        self.yaw ,self.pitch ,self.roll = self.Gimbal.getAttitude()
        
    def makeZero(self):
        self.yaw, self.pitch = 0, 0
    
    def findCenterPoint(self,Frameheight, Framewidth):
        centerX = Framewidth//2
        centerY = Frameheight//2
        return centerX, centerY
    
    def setResolution(self, height:int,width:int):
        self.ScreenHeight = height
        self.ScreenWidth = width
        self.CenterX, self.CenterY = self.findCenterPoint(self.ScreenHeight,self.ScreenWidth)

    def setField_of_view(self, HFOV,VFOV):
        self.HFOV = HFOV
        self.VFOV = VFOV

    def setArrowMoves(self,Arrow):
        match Arrow:
            case "Left":
                self.setMoveSteps(10,0)
            case "Right":
                self.setMoveSteps(-10,0)
            case "Up":
                self.setMoveSteps(0,10)
            case "Down":
                self.setMoveSteps(0,-10)

    def setLimts(self, min_yaw:int,max_yaw:int,min_pitch:int,max_pitch:int):
        self.MIN_YAW = min_yaw
        self.MAX_YAW = max_yaw
        self.MIN_PITCH =min_pitch
        self.MAX_PITCH =max_pitch

    # This Function Generate Current position to need position yaw , pitch
    def findPitchAndYaw(self,SelectedPoint:tuple):
        cX,cY = self.CenterX,self.CenterY
        selectedX,selectedY = SelectedPoint
        delta_x = selectedX - cX
        delta_y = selectedY - cY

        yaw = -delta_x * (self.HFOV /self.ScreenWidth)
        pitch = -delta_y * (self.VFOV /self.ScreenHeight)
        
        return round(yaw, 1) , round(pitch, 1)
    
    def isPossibleMove(self, need_yaw,need_pitch):
        desired_yaw =self.yaw + need_yaw
        desired_pitch = self.pitch + need_pitch
    
        if desired_pitch >= self.MIN_PITCH and desired_pitch <= self.MAX_PITCH and desired_yaw <= self.MAX_YAW and desired_yaw >= self.MIN_YAW:
   
            return True
        
        
        return False
    
        


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
        self.yaw ,self.pitch ,self.roll = self.Gimbal.getAttitude()
    
    def updateRotation(self):
        self.yaw ,self.pitch ,self.roll = self.Gimbal.getAttitude()
        FlagChange = False
        if self.yaw < self.MIN_YAW:
            self.yaw = self.MIN_YAW
            FlagChange = True
        elif self.yaw > self.MAX_YAW:
            self.yaw = self.MAX_YAW
            FlagChange = True
        
        if self.pitch <self.MIN_PITCH:
            self.pitch = self.MIN_PITCH
            FlagChange = True
        elif self.pitch > self.MAX_PITCH:
            self.pitch = self.MAX_PITCH
            FlagChange = True
        
        if FlagChange:
            self.Gimbal.setGimbalRotation(self.yaw,self.pitch)

        
        return self.yaw , self.pitch , self.roll
    

    
    def centerGimbal(self):
        self.Gimbal.requestCenterGimbal()

    def getShape(self):
        return self.ScreenHeight, self.ScreenWidth
    
    def getCenter(self):
        return self.CenterX, self.CenterY





    

def findPitchAndYaw(cX,cY,selectedX,selectedY,frameHeight,frameWidth,HFOV=81,VFOV=52):
    delta_x = selectedX - cX
    delta_y = selectedY - cY

    yaw = -delta_x * (HFOV / frameWidth)
    pitch = -delta_y * (VFOV / frameHeight)

    return yaw , pitch


def pixel_to_angle(pixel_x,pixel_y,focal_length_mm,sensor_width,sensor_height,image_width,image_height,center_x,center_y,current_pitch,current_yaw):
    """
    Converts pixel coordinates to angular displacement (degrees) from the center of the image, taking into account the initial gimbal angles.

    Args:
    - pixel_x, pixel_y: Pixel coordinates to be centered.
    - focal_length_mm: Focal length of the camera in millimeters.
    - sensor_width, sensor_height: Physical dimensions of the sensor in millimeters.
    - image_width, image_height: Dimensions of the image in pixels.
    - center_x, center_y: Center pixel coordinates (usually the center of the image).
    - current_pitch, current_yaw: Current pitch and yaw angles of the gimbal.

    Returns:
    - new_pitch, new_yaw: Updated gimbal angles to center the pixel.
    """

    # Convert focal length from mm to pixels
    focal_length_x = (focal_length_mm * image_width) / sensor_width
    focal_length_y = (focal_length_mm * image_height) / sensor_height

    # Calculate normalized coordinates
    norm_x = (pixel_x - center_x) / focal_length_x
    norm_y = (pixel_y - center_y) / focal_length_y

    # Calculate angles in radians
    angle_x_rad = math.atan(norm_x)
    angle_y_rad = math.atan(norm_y)

    # Convert angles to degrees
    angle_x_deg = math.degrees(angle_x_rad)
    angle_y_deg = math.degrees(angle_y_rad)

    # Update gimbal angles
    new_pitch = current_pitch + angle_y_deg
    new_yaw = current_yaw + angle_x_deg

    return new_pitch, new_yaw


  