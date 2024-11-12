import cv2 
import numpy as np 
import os, sys,threading, queue, math, csv
from pymavlink import mavutil
import time 
from datetime import datetime
import simplekml
import Footprint_MIT as FP
import math
from a8_utils import Camera 
import shutil

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)

sys.path.append(parent_directory)

from siyi_sdk import SIYISDK

master = mavutil.mavlink_connection("udpin:0.0.0.0:14550", baud=115200, autoreconnect=True)
master.wait_heartbeat()
master.mav.heartbeat_send(
    mavutil.mavlink.MAV_TYPE_QUADROTOR,    # MAV_TYPE
    mavutil.mavlink.MAV_AUTOPILOT_GENERIC, # Autopilot type
    0,                                     # Base mode
    0,                                     # Custom mode
    mavutil.mavlink.MAV_STATE_ACTIVE       # System status
)

print("Heartbeat from system (system %u component %u)" % (master.target_system, master.target_component))

Actual_Target =[13.3896903,80.2300828] #lat ,lng
mod_lat, mod_lng, rel_alt, mod_yaw_angle, mod_roll, mod_pitch= 0,0,0,0,0,0
# Initialize a frame counter
f =0
zoomlevel =0


font =cv2.FONT_HERSHEY_SIMPLEX

''' Gobal variable '''
target_cordinates = [0.0,0.0] #lat , lng
point_selected =False
p0 =None
old_gray = None
boundBox =None
HFOV =81
VFOV =52
TARGET_FLAG = False


flag, flag1 = 0,0
sensor_width, sensor_height = (37.706, 21.226)
focal_length = 21

# Sensor_Width=2 * focal_length * math.tan(HFOV/2)
# Sensor_Height=2 * focal_length * math.tan(VFOV/2)

Ls = float(sensor_width)
Hs = float(sensor_height)
f = float(focal_length)
rad1 = np.pi / 180

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
reportpath = f"a8_gimbal_report_{timestamp}"
os.makedirs(reportpath+"/img")





b="rtsp://192.168.6.121:8554/main.264"
pipline =f'rtspsrc location={b} latency=0 ! decodebin ! videoconvert ! appsink'

cap = cv2.VideoCapture(pipline, cv2.CAP_GSTREAMER)

cam=SIYISDK(server_ip="192.168.6.121", port=37260)
if not cam.connect():
    print("No connection ")
    exit(1)

cam.requestFollowMode()





gimbalCamera = Camera(cam)


if cap.isOpened():
    ret , frame = cap.read()
    h,w,_ = frame.shape
    gimbalCamera.setResolution(h,w)
    gimbalCamera.setField_of_view(HFOV,VFOV)
    gimbalCamera.setLimts(-120.0,120.0,-85.0,22.0)
    
else:
    print("Unable Present Video")


gimbal_queue = queue.Queue()
gimbal_running = True
gimbal_buzzy =False


def gimbal_controller():
    global gimbal_running, gimbal_buzzy
    while gimbal_running:
        try:
            
            yaw, pitch = gimbal_queue.get(timeout=0.5)
            gimbal_buzzy =True
            gimbalCamera.setMoveSteps(yaw,pitch)
            
            gimbal_buzzy = False
        except queue.Empty:
            continue

gimbal_thread =threading.Thread(target=gimbal_controller,daemon=True)
gimbal_thread.start()

def stop_gimbal_thread():
    global gimbal_running
    gimbal_running = False
    gimbal_thread.join()


print("Current motion mode: ", cam._motionMode_msg.mode)

def select_point(event, x,y,flags,param):
    
    global point_selected, p0, boundBox,TARGET_FLAG,TARGET_LOCK
    global font, target_cordinates
    if event == cv2.EVENT_LBUTTONDOWN:
        
        point = (x,y)
        point_selected = True
        p0 = np.array([[x,y]], dtype=np.float32)
        boundBox = (x-50, y-50,100,100)
        TARGET_FLAG = True
        yaw, pitch =gimbalCamera.findPitchAndYaw(point)
        if gimbalCamera.isPossibleMove(yaw,pitch):
            gimbal_queue.put((yaw,pitch))
            yaw,pitch,roll = gimbalCamera.Gimbal.getAttitude()
            target_cordinates[0], target_cordinates[1] = getTargetCoordinates(x,y,pitch,yaw)

cv2.namedWindow("Tracking Window",cv2.WND_PROP_FULLSCREEN)
cv2.setMouseCallback("Tracking Window", select_point)

def vehicle_location():
    global master, mod_lat, mod_lng, rel_alt, mod_yaw_angle, mod_roll, mod_pitch, flag, flag1
    # if !initial1:
    while True:
        if flag and flag1:
            break
        msg = master.recv_match()
        if not msg:
            

            mod_lat = mod_lat
            mod_lng = mod_lng
            rel_alt = rel_alt
            mod_yaw_angle = mod_yaw_angle
            continue
        if msg.get_type() == "GLOBAL_POSITION_INT":
            mod_lat = master.field("GLOBAL_POSITION_INT", "lat", 0) * 1.0e-7
            mod_lng = master.field("GLOBAL_POSITION_INT", "lon", 0) * 1.0e-7
            rel_alt = master.field("GLOBAL_POSITION_INT", "relative_alt", 0) * 1.0e-3
        if msg.get_type() == "ATTITUDE":
            yaw = master.field("ATTITUDE", "yaw", 0)
            mod_pitch = master.field("ATTITUDE", "pitch", 0)
            mod_roll = master.field("ATTITUDE", "roll", 0)
            pitch_deg = math.degrees(mod_pitch)
            roll_deg = math.degrees(mod_roll)
            yaw_1 = math.degrees(yaw)
            yaw_2 = 360 + yaw_1
            if yaw_2 > 360:
                mod_yaw_angle = yaw_2 - 360
            else:
                mod_yaw_angle = yaw_2
            mod_lat = mod_lat
            mod_lng = mod_lng
            mod_roll = roll_deg
            mod_pitch = pitch_deg
            yaw = mod_yaw_angle
            rel_alt = rel_alt
           

        
        


def draw_plus_point(frame,points,arm_length,color,thickness):
    cenX,cenY = points
    
    cv2.line(frame, (int(cenX), int(cenY - arm_length)), (int(cenX), int(cenY + arm_length)), color, thickness)
    cv2.line(frame, (int(cenX - arm_length),int(cenY)), (int(cenX + arm_length), int(cenY)), color, thickness)




def draw_resizable_focus_rect(frame, pt1, pt2, color=(0, 255, 0), thickness=2, scale_factor=0.1):

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


def distance_bearing(homeLattitude, homeLongitude, destinationLattitude, destinationLongitude):
    R = 6371e3 #Radius of earth in metres
    rlat1 = homeLattitude * (math.pi/180)
    rlat2 = destinationLattitude * (math.pi/180) 
    rlon1 = homeLongitude * (math.pi/180) 
    rlon2 = destinationLongitude * (math.pi/180) 
    dlat = (destinationLattitude - homeLattitude) * (math.pi/180)
    dlon = (destinationLongitude - homeLongitude) * (math.pi/180)
    #haversine formula to find distance
    a = (math.sin(dlat/2) * math.sin(dlat/2)) + (math.cos(rlat1) * math.cos(rlat2) * (math.sin(dlon/2) * math.sin(dlon/2)))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c #distance in metres
    #formula for bearing
    y = math.sin(rlon2 - rlon1) * math.cos(rlat2)
    x = math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(rlon2 - rlon1)
    bearing = math.atan2(y, x) #bearing in radians
    bearingDegrees = bearing * (180/math.pi)
    out = [distance, bearingDegrees]
    return out

def getTargetCoordinates(target_x,target_y,cam_yaw,cam_pitch):
    global mod_lat,mod_lng,rel_alt,mod_yaw_angle,Ls,Hs,f,mod_roll,rad1,gimbalCamera

    Screen_height,Screen_width= gimbalCamera.getShape()
    target_lat, target_lon = FP.getPos(mod_lat,mod_lng,rel_alt,mod_yaw_angle,Ls,Hs,f,cam_pitch,0,target_x,target_y,rad1,Screen_width,Screen_height)

            
    return  target_lat, target_lon

      
cv2.namedWindow("Tracking Window",cv2.WND_PROP_FULLSCREEN)
cv2.setMouseCallback("Tracking Window", select_point)

        
       


def findCenterPoint(Frameheight, Framewidth):
    centerX = Framewidth//2
    centerY = Frameheight//2
    return centerX, centerY




print(f"Frame Height:{gimbalCamera.ScreenHeight}, Width: {gimbalCamera.ScreenWidth}")
lk_params = dict(winSize = (15,15), maxLevel=2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03))
index_frame =0

def main():
    global index_frame, old_gray,p0,p1,point_selected,font,mod_lat,mod_lng,mod_pitch,mod_yaw_angle
    global TARGET_FLAG,gimbal_buzzy, target_cordinates, reportpath
    global Actual_Target, zoomlevel
    kml = simplekml.Kml()
    pnt = kml.newpoint()
    pnt.coords = [(Actual_Target[1], Actual_Target[0], 0.0)] 
    pnt.altitudemode = simplekml.AltitudeMode.relativetoground
    pnt.name = f"Target Point Location"
    
    Screen_height,Screen_width= gimbalCamera.getShape()
    cenX ,cenY = gimbalCamera.getCenter()

    while cap.isOpened():
        ret , frame = cap.read()

        if not ret:
            break
        # frame = cv2.resize(frame,(1280,720))
        
        if index_frame%30 == 0 or index_frame == 0:
            curr_yaw,curr_pitch,roll = gimbalCamera.Gimbal.getAttitude()

        
        
    
        
        
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        

        if point_selected:
            
            if old_gray is not None:
                p1, st,err = cv2.calcOpticalFlowPyrLK(old_gray,frame_gray,p0,None,**lk_params)

                if st[0] ==1:
                    x, y  = p1.ravel()
                    p0 = p1
                    x1, y1 = int(x-30), int(y-30)
                    x2, y2 = int(x + 30), int(y + 30)
                    yaw, pitch = gimbalCamera.findPitchAndYaw((x,y))
                    if abs(int(yaw)) > 0 and abs(int(pitch)) > 0 :
                        if not gimbalCamera.isPossibleMove(yaw,pitch):
                            draw_plus_point(frame,(x,y),5,(0,0,255),1)
                            
                            draw_resizable_focus_rect(frame,(x1,y1),(x2,y2),(0,0,255),2)
                            #curr_yaw,curr_pitch,roll = gimbalCamera.updateRotation()
                            target_cordinates[0], target_cordinates[1] = getTargetCoordinates(x,y,curr_pitch,curr_yaw)
                            TARGET_FLAG = False
                        else:
                            draw_plus_point(frame,(x,y),5,(0,255,0),1)
                            
                            draw_resizable_focus_rect(frame,(x1,y1),(x2,y2),(0,255,0),2)
                            # curr_yaw,curr_pitch,roll = gimbalCamera.updateRotation()
                            target_cordinates[0], target_cordinates[1] = getTargetCoordinates(x,y,curr_pitch,curr_yaw)
                            

                    
                        if index_frame%20 == 0 and TARGET_FLAG:
                            print("@@@","Need Yaw:",str(yaw),"Need Pitch: ",str(pitch))
                            if not gimbal_buzzy:
                                gimbal_queue.put((yaw,pitch))
                    else:
                        draw_plus_point(frame,(x,y),5,(0,255,255),2)
                        draw_resizable_focus_rect(frame,(x1,y1),(x2,y2),(0,255,255),2)
                        

                        #curr_yaw,curr_pitch,roll = gimbalCamera.updateRotation()
                        target_cordinates[0], target_cordinates[1] = getTargetCoordinates(x,y,curr_pitch,curr_yaw)


                    

            old_gray = frame_gray.copy()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        distance = distance_bearing(Actual_Target[0],Actual_Target[1],target_cordinates[0],target_cordinates[1])
        draw_plus_point(frame,(cenX,cenY),20,(0,0,255),1)
        cv2.putText(frame,f"yaw: {curr_yaw} , pitch:{curr_pitch} roll: {roll}",(Screen_width-300,20),font,0.5,(255,0,0),2)
        cv2.putText(frame,f"Actual Target Location: {Actual_Target[0]},{Actual_Target[1]}",(10,20), font,0.5,(255,0,255),2)
        cv2.putText(frame,f"Error Distance:{distance[0]:.2f}",(10,Screen_height-50), font,0.5,(255,0,255),2)
        cv2.putText(frame,f"Model Altitude: {rel_alt:.2f} m",(10,Screen_height-20), font,0.5,(255,0,255),2)
        cv2.putText(frame,f"Model Location: {mod_lat} , {mod_lng}",(Screen_width-500,Screen_height-50), font,0.5,(255,255,0),2)
        cv2.putText(frame,f"Target Location: {target_cordinates[0]}, {target_cordinates[1]}", (Screen_width-500,Screen_height-20), font,0.5,(255,255,0),2)

        
        cv2.imshow("Tracking Window", frame)

        index_frame += 1
        

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == 81:
           if not gimbal_buzzy:
                gimbal_queue.put((10,0))
                continue
        

        elif key == 83:
            if not gimbal_buzzy:
                gimbal_queue.put((-10,0))
                continue

        elif key == 82:
            if not gimbal_buzzy:
                gimbal_queue.put((0,7))
                continue

        elif key == 84:
            if not gimbal_buzzy:
                gimbal_queue.put((0,-7))
                continue

        elif key == ord('c'):
            #center the camera
            while not gimbal_queue.empty():
                gimbal_queue.get(timeout=0.2)
            gimbalCamera.centerGimbal()
            
            TARGET_FLAG = False
            point_selected =False
            old_gray =None
            p0 =None
            p1 = None
            
            continue
     

        elif key == ord("v"):
    
            if cam.requestFPVMode():
                print("FPV Mode Activated")

        elif key == ord("l"):
            if cam.requestLockMode():
                print("Lock Mode Activated")
        
        elif key == ord("f"):
            if cam.requestFollowMode():
                print("Follow Mode Activated")
        elif key == ord("a"):
            if cam.requestFocusHold():
                print("Manual Focus")

        elif key  == ord("z"):
            zoomlevel  =zoomlevel+1
            if cam.requestAbsoluteZoom(zoomlevel):
                print("Level of Zoom"+str(zoomlevel))
        elif key == ord("x"):
            zoomlevel =zoomlevel-1
            if cam.requestAbsoluteZoom(zoomlevel):
                print("Zoom out "+str(zoomlevel))
            
        elif key == ord("r"):
            pnt = kml.newpoint()
            pnt.coords = [(mod_lng, mod_lat, rel_alt)] 
            pnt.altitudemode = simplekml.AltitudeMode.relativetoground
           
            
            pnt.name = f"Err Dist:{distance[0]:.1f} m"
            image_path= f'./{reportpath}/img/a8_mini_gimbal_out_{timestamp}.jpg'
            img_src = f'./img/a8_mini_gimbal_out_{timestamp}.jpg'
            cv2.imwrite(image_path, frame)
            description = f"""Model Location:{mod_lat},{mod_lng} <br>
                Actual Target Location: {Actual_Target[0]} ,{Actual_Target[1]} to Detected Target Coordinates: {target_cordinates[0]}, {target_cordinates[1]} <br>
                Error Distance: {distance[0]:.2f} meters <br>
                <img src={img_src} alt="A8_testing" width={Screen_width*0.4} height={Screen_height*0.4}>
                """
            
            pnt.description =description
            continue
        key = cv2.waitKey(1)
        

    kml.save(f"./{reportpath}/output.kml")
    cap.release()
    
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    try:
        threading.Thread(target=vehicle_location).start()
        main()
        
    finally:
        # Stop the gimbal control thread
        stop_gimbal_thread()



