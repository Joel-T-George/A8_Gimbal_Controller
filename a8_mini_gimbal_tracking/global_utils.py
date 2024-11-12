class GlobalUtils():
    def __init__(self) -> None:
        self.Video_url = ""
        self.Mavlink_out = ""
        self.Mavlink_baud = 0
        self.GimbalIP=""
        self.GimbalPort = 0

    

    def getVideoUrl(self):
        if self.Video_url == "":
            print("Video URL Not Provided")
        else:
            return self.Video_url
        
        return "Invalid Activity Founded"