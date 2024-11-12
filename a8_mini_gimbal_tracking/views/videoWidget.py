import customtkinter as ctk
import cv2
import numpy as np

from PIL import Image

class VideoFrame(ctk.CTkFrame):
    def __init__(self, master,GimbalControl=None,VideoControl=None,**kwargs):
        super().__init__(master, **kwargs)
        self.ImageHeight, self.ImageWidth = 0,0
        self.IndexFrame =0
        self.GimbalControl = GimbalControl
        self.VideoControl = VideoControl
        self.clicked_x, self.clicked_y = None,None
        self.StreamingFlag = False
        self.clicked_flag =False
        self.old_gray = None
        self.HFOV = 81
        self.VFOV = 52
        self.p0= None
        self.lk_params = dict(winSize = (15,15), maxLevel=2, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03))
    
        self.video_label = ctk.CTkLabel(self, text="", cursor="cross")
        self.video_label.pack(fill="both",expand=True)
        self.VideoControl.setStreammingUrl("rtsp://192.168.6.121:8554/main.264")
        #self.VideoControl.setStreammingUrl(0)
        if self.VideoControl.intializeStreaming():
            self.StreamingFlag = True
            print("Video Streaming intialized")

        self.ImageHeight, self.ImageWidth = self.VideoControl.getShape()

        self.VideoControl.startStreaming()

        self.GimbalControl.setGimbalIp(("192.168.6.121",37260))
        if self.GimbalControl.intializeGimbal():
            print("Gimbal Intialized")

        if self.StreamingFlag:
            self.GimbalControl.setResolution(self.ImageHeight,self.ImageWidth)
            self.GimbalControl.setField_of_view(self.HFOV,self.VFOV)
            self.GimbalControl.setLimts(-120.0,120.0,-85.0,22.0)


        self.GimbalControl.startGimbalControl()
    
       
        self.VideoStreaming()
        self.bind("<Configure>",self.on_resize)
        self.video_label.bind("<Button-1>",self.on_click)
        self.video_label.bind("<Control-r>",self.display_ROI)
       
    def set_clicked(self,x,y):
        self.clicked_x,self.clicked_y = x,y

    
    def display_ROI(self):
        pass
        
    
    def VideoStreaming(self):
        if self.StreamingFlag:
            ret, frame = self.VideoControl.getFrame()
       
            if ret:
                VideoFrameWidth = self.video_label.winfo_width()
                VideoFrameHeight = self.video_label.winfo_height()

            if self.VideoControl.isTargetLocked() and (self.IndexFrame == 0 or self.IndexFrame % 5 == 0 ):
                Target_x, Target_y = self.VideoControl.getTargetCenterCoords()
                if Target_x is not None:
                    yaw, pitch = self.GimbalControl.findPitchAndYaw((Target_x, Target_y))
                    if abs(int(yaw)) > 0 and abs(int(pitch)) > 0:
                        self.GimbalControl.gimbalMove("need",yaw,pitch)



            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            if VideoFrameWidth > 0  and VideoFrameHeight >0:
                resized_frame, self.padding_x,self.padding_y = self.dyanamic_resize_image(frame, VideoFrameWidth, VideoFrameHeight)
                img = Image.fromarray(resized_frame)

                imgtk = ctk.CTkImage(light_image=img, dark_image=img,size=img.size)
                self.video_label.configure(image=imgtk)
                self.video_label.imgtk = imgtk
                self.IndexFrame = self.IndexFrame +1
            
        self.after(1,self.VideoStreaming)


    def on_resize(self,event):
        self.video_label.update_idletasks()

    def on_click(self, event):
        self.clicked_flag = True
        click_x, click_y = event.x, event.y

        # Get the displayed image dimensions (as resized within the CTkLabel)
        displayed_width = self.video_label.winfo_width()
        displayed_height = self.video_label.winfo_height()

        adjusted_x_click =click_x-self.padding_x
        adjusted_y_click = click_y-self.padding_y
        # Map the clicked coordinates to the original image dimensions
        original_x = int(adjusted_x_click * (self.ImageWidth / (displayed_width - 2 * self.padding_x)))
        original_y = int(adjusted_y_click * (self.ImageHeight / (displayed_height -2 * self.padding_y)))

        self.VideoControl.selectedCoord(original_x,original_y)
        # self.p0 = np.array([[original_x,original_y]], dtype=np.float32)


    def dyanamic_resize_image(self, frame, max_width, max_height):
        """Resize image while maintaining the aspect ratio."""
        # Get original dimensions
        # Calculate the aspect ratio of the video
        aspect_ratio = self.ImageWidth / self.ImageHeight
        
        # Calculate the new width and height based on the window size while maintaining aspect ratio
        if max_width / max_height > aspect_ratio:
            # Width is too large for the given height; adjust width
            new_height = max_height
            new_width = int(aspect_ratio * new_height)
        else:
            # Height is too large for the given width; adjust height
            new_width = max_width
            new_height = int(new_width / aspect_ratio)


        padding_x = (max_width-new_width)//2
        padding_y = (max_height-new_height)//2

        # Ensure new_width and new_height are greater than zero
        if new_width > 0 and new_height > 0:
            # Resize the frame using the calculated new dimensions
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            padded_frame = cv2.copyMakeBorder(resized_frame, padding_y, padding_y, padding_x, padding_x, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            return padded_frame, padding_x,padding_y
        else:
            return frame  , padding_x,padding_y# If the dimensions invalid, return the original frame
        
    def on_closing(self):
        # Release the video capture and destroy the window
        self.VideoControl.destroy()
        
