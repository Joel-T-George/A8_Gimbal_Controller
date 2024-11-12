import customtkinter as ctk

class ControlPanel(ctk.CTkFrame):
    def __init__(self,master,GimbalControl=None,VideoControl=None,**kwargs):
        super().__init__( master,**kwargs)
        self.Gimbal = GimbalControl
        self.VideoControl =VideoControl
        font = ctk.CTkFont(family="Arial",size=18, weight="bold")
        self.DirectionControlPanel = ctk.CTkFrame(master=self)
        self.DirectionControlPanel.pack(fill="both", expand=True)

        self.btn_up =ctk.CTkButton(master=self.DirectionControlPanel, text="Up", width=100,height=50,font=font, cursor ="hand2", command=self.moveUpButton)
        self.btn_down =ctk.CTkButton(master=self.DirectionControlPanel, text="Down",width=100,height=50,font=font,cursor ="hand2", command=self.moveDownButton)
        self.btn_left =ctk.CTkButton(master=self.DirectionControlPanel, text="Left",width=100,height=50,font=font,cursor ="hand2", command=self.moveLeftButton)
        self.btn_right =ctk.CTkButton(master=self.DirectionControlPanel, text="Right",width=100,height=50, font=font,cursor ="hand2", command=self.moveRightButton)
        self.btn_home =ctk.CTkButton(master=self.DirectionControlPanel, text="Home",width=100,height=50, font=font,cursor ="hand2", command=self.moveHomeButton)

        self.btn_up.grid(row=0, column=1, padx=10, pady=10)      
        self.btn_left.grid(row=1, column=0, padx=10, pady=10)    
        self.btn_home.grid(row=1, column=1, padx=10, pady=10)    
        self.btn_right.grid(row=1, column=2, padx=10, pady=10)   
        self.btn_down.grid(row=2, column=1, padx=10, pady=10)   

        self.ZoomControlPanel = ctk.CTkFrame(master=self) 
        self.ZoomControlPanel.pack(fill="both", expand=True)

        self.btn_zoom_in = ctk.CTkButton(master=self.ZoomControlPanel, text="Zoom In",width=100,height=50, font=font, cursor="hand2", command=self.moveZoomINButton)
        self.btn_zoom_out = ctk.CTkButton(master= self.ZoomControlPanel, text="Zoom Out",width=100,height=50, font=font, cursor="hand2",command=self.moveZoomOUTButton)
        self.btn_zoom_in.grid(row= 0, column=0, padx=10, pady=10)
        self.btn_zoom_out.grid(row=0,column=1, padx=10, pady=10)


    def moveUpButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.gimbalMove("need",0,7)
        

    def moveDownButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.gimbalMove("need",0,-7)

    def moveRightButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.gimbalMove("need",-10,0)

    def moveLeftButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.gimbalMove("need",10,0)

    def moveHomeButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.gimbalMove("direct",0,0)
        self.Gimbal.centerGimbal()
        

    def moveZoomINButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.GimbalZoomIN()

    def moveZoomOUTButton(self):
        self.VideoControl.resetTracker()
        self.Gimbal.GimbalZoomOut()