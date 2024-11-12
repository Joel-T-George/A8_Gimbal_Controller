import customtkinter as ctk
from .videoWidget import VideoFrame
from .controlWidget import ControlPanel

from .settingsWidget import SettingPanel

class TabView(ctk.CTkTabview):
    def __init__(self, master,GimbalControl=None,VideoControl=None,**kwargs):
        super().__init__(master, **kwargs)
        

        # create tabs
        self.add("Home")
        self.add("Settings")
    

        # add widgets on tabs
        

        self.video = VideoFrame(master=self.tab("Home"),GimbalControl=GimbalControl,VideoControl=VideoControl)
        self.video.pack(side="left",fill="both", expand=True, padx=10,pady=10)

        self.controlPanel = ControlPanel(master=self.tab("Home"), GimbalControl=GimbalControl,VideoControl=VideoControl)
        self.controlPanel.pack(side="right",fill="both",expand=True, padx=10,pady=10 )
        



        self.settingPanel =SettingPanel(master=self.tab("Settings"), GimbalControl=GimbalControl, VideoControl=VideoControl)
        self.settingPanel.pack(fill="both", expand=True, padx=10,pady=10)

        self._segmented_button.grid(row=0, column=0, sticky="nw", padx=0, pady=1)
        for tab in self._segmented_button._buttons_dict.values():
            tab.configure(width=100, height=50, font=("Arial", 16)) 

