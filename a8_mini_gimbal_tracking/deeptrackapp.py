import sys, os
sys.path.append('/home/dhaksha/Documents/a8_sdk_control_learning/siyi_sdk/a8_mini_gimbal_tracking/SiamMask')

from genericpath import isfile
import time
import torch
import json
import numpy as np
import cv2
from SiamMask.utils.config_helper import load_config
from SiamMask.utils.load_helper import load_pretrain
from SiamMask.tools.test import siamese_init , siamese_track
b="rtsp://192.168.6.121:8554/main.264"
pipline =f'rtspsrc location={b} latency=0 ! decodebin ! videoconvert ! appsink'
cap=cv2.VideoCapture(pipline, cv2.CAP_GSTREAMER)

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

arg = {
    "config":"./SiamMask/experiments/siammask_sharp/config_davis.json",
    "checkpoint": "./SiamMask/SiamMask_DAVIS.pth"
}
class obj:
     
    # constructor
    def __init__(self, dict1):
        self.__dict__.update(dict1)

def selectROI_activate(currentFrame):
    init_rect = cv2.selectROI('SiamMask Selector', currentFrame, fromCenter=True, showCrosshair=True)
    if init_rect != (0, 0, 0, 0):
        
        return init_rect




args = json.loads(json.dumps(arg),object_hook=obj)
if __name__ == '__main__':
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.backends.cudnn.benchmark = True

    cfg = load_config(args)
    from SiamMask.experiments.siammask_sharp.custom import Custom
    siammask = Custom(anchors = cfg['anchors'])
    assert isfile(arg["checkpoint"])
    siammask = load_pretrain(siammask,args.checkpoint)
    siammask.eval().to(device)


    cv2.namedWindow("SiamMask Selector", cv2.WND_PROP_FULLSCREEN)
    selection_flag =False
    selection_Completed = False
    frame = "I will give"
   
    print(cv2.__version__)
    if cap.isOpened():
        time.sleep(2)
        ret,track_frame =cap.read()
        index_frame =0
        
        if track_frame is None:
            print("Error: Could not load the image")
        else:
           while True:
                if index_frame %30 ==0:
                    init_rect = cv2.selectROI('SiamMask Selector', track_frame, fromCenter=False, showCrosshair=True)
                    if init_rect != (0, 0, 0, 0):
                        x, y, w, h = init_rect
                        selection_flag = True
                        print(f"ROI Selected: {x}, {y}, {w}, {h}")
                        cv2.destroyWindow("SiamMask Selector")
                        break
                elif cv2.waitKey(0) & 0xFF == ord('c'):  # Press 'c' to cancel selection
                    print("Selection canceled by user")
                    selection_flag = False
                    break
                index_frame += 1
            

 
        
    prev_time = time.time()   
    
    index_frame =0 
    while cap.isOpened():
        
        ret , frame = cap.read()
        track_frame = frame
        if not ret:
            break

        

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        if selection_flag and not selection_Completed:
            target_pos = np.array([x + w / 2, y + h / 2])
            target_sz = np.array([w, h])
            state = siamese_init(track_frame, target_pos, target_sz, siammask, cfg['hp'], device=device)
            # Initialize mask for comparison
            init_mask = np.zeros_like(frame)
            init_mask[y:y+h, x:x+w] = 1
            selection_Completed =True

        if selection_Completed:
            state = siamese_track(state, frame, mask_enable=True, refine_enable=True, device=device)
            location = state['ploygon'].flatten()
            mask = state['mask'] > state['p'].seg_thr
            frame[:, :, 2] = (mask > 0) * 255 + (mask == 0) * frame[:, :, 2]
            cv2.polylines(frame, [np.int32(location).reshape((-1, 1, 2))], True, (0, 255, 0), 3)
            #print(state['p'].__dict__.keys()) 

            # Calculate IoU for confidence
            current_mask = np.zeros_like(frame)
            current_mask[mask] = 1
            intersection = np.sum(init_mask & current_mask)
            union = np.sum(init_mask | current_mask)
            iou = intersection / union if union > 0 else 0
            confidence = iou  # Using IoU as a proxy for confidence
            cv2.putText(frame, f'Confidence: {confidence:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.putText(frame, f'FPS: {fps:.2f}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        cv2.imshow('SiamMask', frame)
        index_frame =+ 1

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break
        elif cv2.waitKey(30) & 0xFF == ord('r'):
            init_rect = cv2.selectROI('SiamMask Selector', frame, fromCenter=False, showCrosshair=True)
            if init_rect != (0, 0, 0, 0):
                x, y, w, h = init_rect
                selection_flag = True
                selection_Completed = False
                print(f"ROI Selected: {x}, {y}, {w}, {h}")
                cv2.destroyWindow("SiamMask Selector")
                continue
        
