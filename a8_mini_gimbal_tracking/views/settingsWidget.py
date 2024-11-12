import customtkinter as ctk


class SettingPanel(ctk.CTkFrame):
    def __init__(self, master,GimbalControl=None,VideoControl=None,**kwargs):
        super().__init__(master, **kwargs)

        self.videoSettings = ctk.CTkFrame(master= self)
        self.videoSettings.pack(fill="both", expand=True,padx=10,pady=10)



        self.videoUrlLabel = ctk.CTkLabel(master=self.videoSettings, text="Network Stream:")
        self.videoUrlLabel.grid(row=0,column=0, padx=10,pady=10)

        self.videoUrl  = ctk.CTkEntry(master=self.videoSettings, placeholder_text="Video Url")
        self.videoUrl.grid(row=0,column =1, padx=10,pady=10)

        self.videoConnectBtn = ctk.CTkButton(master=self.videoSettings, command=self.getvideoUrl, text="Connect")
        self.videoConnectBtn.grid(row=0,column=2, padx=10, pady=10)

        self.cameraSettings = ctk.CTkFrame(master=self)
        self.cameraSettings.pack(fill="both",expand=True,padx=10,pady=10)



        self.GimbalConnLabel = ctk.CTkLabel(master=self.cameraSettings, text="Gimbal Address")
        self.GimbalConnLabel.grid(row=0,column=0, padx=10,pady=10)

        self.GimbalIP =ctk.CTkEntry(master=self.cameraSettings,placeholder_text="172.0.0.1")
        self.GimbalIP.grid(row=0,column=1,padx=10,pady=10)

        self.GimbalPort = ctk.CTkEntry(master=self.cameraSettings,placeholder_text="3000")
        self.GimbalPort.grid(row=0,column=2,padx=10,pady=10)

        self.GimbalBtn =ctk.CTkButton(master=self.cameraSettings, text="Connect")
        self.GimbalBtn.grid(row=0,column=3,padx=10,pady=10)

    def getvideoUrl(self):
        print(self.videoUrl.get())