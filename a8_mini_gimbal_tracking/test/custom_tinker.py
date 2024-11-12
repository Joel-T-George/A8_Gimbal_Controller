import tkinter as tk
import customtkinter as ctk
import cv2
from PIL import Image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Resizable Frame with Aspect Ratio")
        self.geometry("800x600")
        self.minsize(400, 300)  # Set a minimum window size

        # Create a frame to contain the video
        self.frame = ctk.CTkFrame(self)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create a CTkLabel for displaying video frames (inside the frame)
        self.video_label = ctk.CTkLabel(self.frame)
        self.video_label.pack(fill="both", expand=True)

        # Start video capture (use '0' for webcam or an RTSP stream)
        self.cap = cv2.VideoCapture(0)  # Replace '0' with an RTSP URL for a stream

        self.original_width = 640  # Set your default video width
        self.original_height = 480  # Set your default video height
        self.stream_video()

        # Bind the configure event to dynamically adjust the video label
        self.bind("<Configure>", self.on_resize)

    def stream_video(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Store the original frame width and height
            self.original_height, self.original_width = frame.shape[:2]

            # Get the current window size
            window_width = self.video_label.winfo_width()
            window_height = self.video_label.winfo_height()

            # Ensure the width and height are valid (greater than zero)
            if window_width > 0 and window_height > 0:
                resized_frame = self.resize_frame(frame, window_width, window_height)
                
                # Convert the OpenCV image to PIL format
                img = Image.fromarray(resized_frame)

                # Use CTkImage with the resized image
                ctk_image = ctk.CTkImage(light_image=img, size=img.size)
                
                # Update the CTkLabel with the new frame
                self.video_label.configure(image=ctk_image)
                self.video_label.imgtk = ctk_image  # Keep a reference to avoid garbage collection

        # Call this function again after a delay to create a video loop
        self.after(10, self.stream_video)

    def resize_frame(self, frame, max_width, max_height):
        """
        Resize the frame while maintaining the aspect ratio, ensuring it fits inside the window.
        """
        # Calculate the aspect ratio of the video
        aspect_ratio = self.original_width / self.original_height
        
        # Calculate the new width and height based on the window size while maintaining aspect ratio
        if max_width / max_height > aspect_ratio:
            # Width is too large for the given height; adjust width
            new_height = max_height
            new_width = int(aspect_ratio * new_height)
        else:
            # Height is too large for the given width; adjust height
            new_width = max_width
            new_height = int(new_width / aspect_ratio)

        # Ensure new_width and new_height are greater than zero
        if new_width > 0 and new_height > 0:
            # Resize the frame using the calculated new dimensions
            resized_frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
            return resized_frame
        else:
            return frame  # If the dimensions are invalid, return the original frame

    def on_resize(self, event):
        # This is triggered when the window is resized
        self.video_label.update_idletasks()

    def on_closing(self):
        # Release the video capture and destroy the window
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
