import tkinter as tk
import customtkinter as ctk
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
from PIL import Image, ImageTk
from functools import partial
from pywinstyles import set_opacity
from audiocraft.models import MusicGen
import threading
from non_gui_func import generate_music, capture_emotions


def get_display_size(): #App dimensions related to screen resolution
    root = ctk.CTk()
    scale = root._get_window_scaling()
    width = int(root.winfo_screenwidth() * 0.8)
    height = int(root.winfo_screenheight() * 0.8)
    x = int(width / 8 * scale)
    y = int(height / 8 * scale)
    root.destroy()
    return width, height, f'{width}x{height}+{x}+{y}'

class App(ctk.CTk):
    def __init__(self, width, height):
        super().__init__()
        self.model = self.initialize_model()
        self.camera_frame = None
        self.music_path = []
    #Window
        self.title("EECS 159")
        self.width = width
        self.height = height
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((0,2), weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        
        self.set_label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=40, weight="bold"))
        self.set_label.grid(row=0, column=2, pady=(20,10))
    #-----------------------------------------Left Sidebar-------------------------------------------------
        self.left_frame_width=int(self.width*0.2)
        self.gesture_label = ctk.CTkLabel(self, text="Gestures", font=ctk.CTkFont(size=40, weight="bold"))
        self.gesture_label.grid(row=0, column=0, pady=(20,10))
        self.left_frame = ctk.CTkFrame(self, width=self.left_frame_width)
        self.left_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
        
        self.left_auto = ctk.CTkButton(self.left_frame, text=f'Automatic Mode', font=ctk.CTkFont(size=30),
                                 width=self.left_frame_width, border_width=2, fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.auto_desc = ctk.CTkTextbox(self.left_frame, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))
        self.auto_desc.insert("end", "When Automatic Mode is selected, the Gesture sound controls will be set automatically according to the generated music")
        self.left_manual = ctk.CTkButton(self.left_frame, text=f'Manual Mode', font=ctk.CTkFont(size=30),
                                 width=self.left_frame_width, border_width=2, fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.manual_desc = ctk.CTkTextbox(self.left_frame, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))
        self.manual_desc.insert("end", "When Manual Mode is selected, the Gesture sound controls will be empty by default. \n\n")
        self.manual_desc.insert("end", "It is up to the user to fill the desired gestures with the respective notes.\n\n")
        self.manual_desc.insert("end", "First the swipe direction will be picked, followed by the amount of fingers, then the sound to be played")

        self.edit_label = ctk.CTkLabel(self.left_frame, text="Edit Gestures", font=ctk.CTkFont(size=30), 
                                       text_color=("gray10", "#DCE4EE"), fg_color="#3B3B3B", corner_radius=5)
        self.edit_label.bind("<Button-1>", self.gesture_page)

        self.left_auto.grid(row=0,column=0,padx=(20,20), pady=(20,10))
        self.auto_desc.grid(row=1, column=0, sticky='nsew', padx=(20,20))
        self.left_manual.grid(row=2,column=0,padx=(20,20), pady=(20,10))
        self.manual_desc.grid(row=3, column=0, sticky='nsew', padx=(20,20))
        self.edit_label.grid(row=4, column=0, sticky='nsew', padx=(20,20), pady=(20,20))

    #--------------------------------------Middle------------------------------------------------
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=1, rowspan=3, padx=(20,20), sticky='nsew')
        self.tabs.add("Audiocraft")
        self.tabs.add("Camera")
        self.tabs.add("Settings")
        self.tabs._segmented_button.configure(border_width=5, corner_radius=10,font=ctk.CTkFont(size=40, weight="bold"))
        #Audiocraft
        self.description = ctk.CTkTextbox(self.tabs.tab("Audiocraft"))
        self.description.grid(row=0, column=0, columnspan=3, sticky='nsew', padx=(10,10), pady=(10,10))
        self.prompt = ctk.CTkEntry(self.tabs.tab("Audiocraft"), width=int(self.width * 0.4), placeholder_text="Music Prompt (Optional)")
        self.prompt.grid(row=2, column=0, columnspan=2, padx=(10, 10), pady=(20, 20), sticky="sew")
        self.genbutton = ctk.CTkButton(self.tabs.tab("Audiocraft"), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), command= lambda:threading.Thread(target=self.genbutton_click).start())
        self.genbutton.grid(row=2, column=2, padx=(10, 10), pady=(20, 20), sticky="sew")

        #Camera
        self.video_label = ctk.CTkLabel(self.tabs.tab("Camera"), width=int(self.width * 0.52), height=int(self.height * 0.7), text="Webcam Feed")
        self.video_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.start_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Start Webcam", command=self.start_webcam)
        self.start_button.grid(row=1, column=0, padx=10, pady=15)

        self.capture_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Capture Webcam")
        self.capture_button.grid(row=1, column=1, padx=10, pady=15)
        
        self.stop_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Stop Webcam", command=self.stop_webcam, state="disabled")
        self.stop_button.grid(row=1, column=2, padx=10, pady=15)

        self.play_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Play", command=self.start_webcam)
        self.play_button.grid(row=2, column=1, padx=10, pady=15)

        self.cap = None
        
    #-------------------------------------------Right Sidebar ------------------------------------------
        self.right_frame = ctk.CTkFrame(self, width=int(self.width * 0.2))
        self.right_frame.grid(row=1, column=2, rowspan=3, sticky="nsew")

    #---------------------------------------------Functions-------------------------------------------------
    def initialize_model(self):
        model = MusicGen.get_pretrained("facebook/musicgen-small")
        model.set_generation_params(duration=7) 
        return model

    def button_click(self, button): #Changes button color when clicked
        button.configure(fg_color="gray30")
    
    def genbutton_click(self):
        self.genbutton.configure(state="disabled")
        if self.cap:
            self.stop_webcam()
            emotions, prompt = capture_emotions(self.camera_frame)
            for emotion, score in emotions.items():
                print(f"**{emotion.capitalize()}**: {score:.2f}%")
            generate_music(self.model, description=prompt)
            self.cap.release()
        elif self.camera_frame is not None:
            emotions, prompt = capture_emotions(self.camera_frame)
            for emotion, score in emotions.items():
                print(f"**{emotion.capitalize()}**: {score:.2f}%")
            generate_music(self.model, description=prompt)
        else:
            self.start_webcam()
            self.stop_webcam()
            self.cap = cv2.VideoCapture(0)
            emotions, prompt = capture_emotions(self.camera_frame)
            for emotion, score in emotions.items():
                print(f"**{emotion.capitalize()}**: {score:.2f}%")
            music_path = generate_music(self.model, description=prompt)
            self.music_path.append(music_path)
        self.genbutton.configure(state="normal")

    def start_webcam(self):
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def stop_webcam(self):
        if self.cap:
            _, self.camera_frame = self.cap.read()
            self.cap.release()
            self.cap = None
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, camera_frame = self.cap.read()
            if ret:
                img = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
                photo = Image.fromarray(img)
                photo_image = ImageTk.PhotoImage(image=photo)
                image_image = ImageTk.getimage(photo_image)
                ctk_image = ctk.CTkImage(image_image, size=((self.width * 0.52),int(self.height * 0.7)))
                self.video_label.configure(image=ctk_image)
                self.video_label.after(15, self.update_frame)  # Update every 15ms

    def gesture_page(self, event):
        self.gesture_frame = ctk.CTkFrame(self, height=self.height, width=self.width,fg_color="black")
        self.gesture_frame.grid(row=0,column=0, rowspan=3,columnspan=3, sticky="nsew")
        set_opacity(self.gesture_frame, value=0.5)
        self.gesture_close = ctk.CTkButton(self, text="X", width=self.width*0.05, font=ctk.CTkFont(size=40, weight="bold"), command=self.remove_gesture_page)
        self.gesture_close.place(relx = 0.95, rely = 0)

    def remove_gesture_page(self):
        self.gesture_frame.grid_remove()
        self.gesture_close.destroy()

width, height, gui_size = get_display_size()
app = App(width, height)
app.geometry(gui_size)
app.resizable(0, 0) #Non resizable window
app.mainloop()
