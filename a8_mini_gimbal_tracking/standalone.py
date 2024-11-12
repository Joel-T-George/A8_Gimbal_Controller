import customtkinter as ctk
from global_utils import GlobalUtils
from features.videocontrol import videoHandler
from features.cameracontrol import cameraGimbalHandler
from views.tabsWidget import TabView as Tab
import os
import sys
"""
    -- A8 Camera Video Showing
        -- Smooth Video Frames without Delay
        -- Enable Video Tracking Controll (Mouse Clicke Control)

    -- Using SDK Control A8 Mini Gimbal
        -- Python SDK Controll Gibmal 

    -- Controll Buttons 
        --Home , Left ,Right,Up , Down Button
        --Zooming 
        --Joystick Controll

    -- AI Tracking
        Selectable Object Trackers -CRST and other
        Interface Yolo Model
        Deep Learning Detection and Tracking

    -- Interface Drone Mavlink
        Get Target Lat Lng, 
        Interface Map

    -- Network and Connection Setting
        Url Changing Option
"""

current = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current)

sys.path.append(parent_directory)


from siyi_sdk import SIYISDK

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.SDK =SIYISDK()
        self.GimbalHandler = cameraGimbalHandler(ControlSDK=self.SDK)
        self.videoHandler = videoHandler()
        self.globalUtils = GlobalUtils()
        self.width = self.winfo_screenwidth()
        self.height= self.winfo_screenheight()

        self.title("A8 Mini Gimbal Controller")
        self.geometry(f"{self.width}x{self.height}")
    

        self.containter =Tab(master =self, GimbalControl=self.GimbalHandler,VideoControl=self.videoHandler)
        self.containter.pack(expand=True, fill="both")
         
    

    def on_closing(self):
        self.containter.video.on_closing()
        self.destroy()
        self.GimbalHandler.destroy()




        
 


