import tkinter as tk
import customtkinter as ctk
import os
os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
import cv2
from PIL import Image, ImageTk
from functools import partial
from audiocraft.models import MusicGen
import threading
import non_gui_func as ngf
import pygame_audio as pa
from client import run_client, close_client


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
        self.pause = 1
        self.emotions = None
        self.success = None
        self.prompt = ""
    #Window
        self.title("Emotion and Gesture Controlled DJ")
        self.width = width
        self.height = height
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((0,2), weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        
        self.set_label = ctk.CTkLabel(self, text="Emotion", font=ctk.CTkFont(size=40, weight="bold"))
        self.set_label.grid(row=0, column=2, pady=(20,10))
    #-----------------------------------------Left Sidebar-------------------------------------------------
        self.left_frame_width=int(self.width*0.2)
        self.gesture_label = ctk.CTkLabel(self, text="Tutorial", font=ctk.CTkFont(size=40, weight="bold"))
        self.gesture_label.grid(row=0, column=0, pady=(20,10))
        self.left_frame = ctk.CTkFrame(self, width=self.left_frame_width)
        self.left_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
        
        self.music_tutorial_label = ctk.CTkButton(self.left_frame, text=f'Music Generation', font=ctk.CTkFont(size=30), state='disabled',
                                 width=self.left_frame_width, border_width=2, fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.music_desc = ctk.CTkTextbox(self.left_frame, height=self.height*0.3, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))
        self.music_desc.insert("end", "Click the Start Webcam Button on the bottom left to get started... Or dont!")
        self.music_desc.insert("end", " If the Webcam is off and the Generate button is clicked, it will briefly turn on to capture an image then stop again right away")
        self.music_desc.insert("end", "\n\nAfter the music is generated, click play and enjoy! The generated music will loop forever until it gets replaced by generating more")
        self.music_desc.configure(state='disabled')
        
        self.gesture_tutorial_label = ctk.CTkButton(self.left_frame, text=f'Gestures', font=ctk.CTkFont(size=30), state='disabled',
                                 width=self.left_frame_width, border_width=2, fg_color="transparent", text_color=("gray10", "#DCE4EE"))
        self.gesture_desc = ctk.CTkTextbox(self.left_frame, height=self.height*0.3, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))        
        self.gesture_desc.insert("end", "With the gesture glove on, press down on any of your 5 fingers to play a sound\n\n")
        self.gesture_desc.insert("end", "The gesture glove has 4 states, determined by swiping in the Left, Right, Up, and Down directions.\n\n")
        self.gesture_desc.insert("end", "Each state will have 5 different unique notes, all of which are also determined by the emotion captured to line up with the music generated.")
        self.gesture_desc.configure(state='disabled')

        self.music_tutorial_label.grid(row=0,column=0, columnspan=2, padx=(20,20), pady=(20,10))
        self.music_desc.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=(20,20))
        self.gesture_tutorial_label.grid(row=2,column=0, columnspan=2, padx=(20,20), pady=(20,10))
        self.gesture_desc.grid(row=3, column=0, columnspan=2, sticky='nsew', padx=(20,20))

        self.start_button = ctk.CTkButton(self.left_frame, text="Start Webcam", fg_color="transparent", border_width=2, 
                                       text_color=("gray10", "#DCE4EE"), command=self.start_webcam)
        self.start_button.grid(row=4, column=0, padx=(10, 10), pady=15)    
        self.stop_button = ctk.CTkButton(self.left_frame, text="Stop Webcam", fg_color="transparent", border_width=2, 
                                       text_color=("gray10", "#DCE4EE"), command=self.stop_webcam, state="disabled")
        self.stop_button.grid(row=4, column=1, padx=(10, 10), pady=15)

    #--------------------------------------Middle------------------------------------------------
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=1, rowspan=3, padx=(20,20), sticky='nsew')
        self.tabs.add("Emotion - Gesture Controlled Music")
        self.tabs._segmented_button.configure(border_width=5, corner_radius=10,font=ctk.CTkFont(size=40, weight="bold"), state='disabled')
        #Emotion - Gesture Controlled Music
        self.tabs.tab("Emotion - Gesture Controlled Music").grid_columnconfigure(1, weight=1)
        self.tabs.tab("Emotion - Gesture Controlled Music").grid_columnconfigure(0, weight=0)
        self.prompt_entry = ctk.CTkEntry(self.tabs.tab("Emotion - Gesture Controlled Music"), width=self.width*0.38, placeholder_text="Music Prompt (Optional)")
        self.prompt_entry.grid(row=2, column=0, columnspan=3, padx=(10, 10), pady=(20, 20), sticky="sew")
        self.genbutton = ctk.CTkButton(self.tabs.tab("Emotion - Gesture Controlled Music"), text="Generate", fg_color="transparent", border_width=2, 
                                       text_color=("gray10", "#DCE4EE"), command= lambda:threading.Thread(target=self.genbutton_click).start())
        self.genbutton.grid(row=2, column=3, padx=(10, 10), pady=(20, 20), sticky="se")

        self.play_button = ctk.CTkButton(self.tabs.tab("Emotion - Gesture Controlled Music"), text="Play / Pause", fg_color="transparent", border_width=2, 
                                       text_color=("gray10", "#DCE4EE"), command= lambda:pa.pause_audio())
        self.play_button.grid(row=3, column=3, padx=(10,10), pady=(10,10), sticky="se")
        self.play_button.configure(state='disabled')

        #Camera
        self.video_label = ctk.CTkLabel(self.tabs.tab("Emotion - Gesture Controlled Music"), width=int(self.width * 0.50), height=int(self.height * 0.67), text="Turn on webcam to get started!")
        self.video_label.grid(row=0, column=0, columnspan=4, padx=(10, 10), pady=(10, 10), sticky='nsew')
        self.cap = None

        #Volume
        self.volume_label = ctk.CTkLabel(self.tabs.tab("Emotion - Gesture Controlled Music"), text="Volume: ", font=ctk.CTkFont(size=20, weight="bold"))
        self.volume_label.grid(row=3, column=0, padx=(10,10), pady=(10,10))
        self.volume_slider = ctk.CTkSlider(self.tabs.tab("Emotion - Gesture Controlled Music"), from_=0.0, to=1.0, number_of_steps=100, command= self.set_volume)
        self.volume_slider.set(0.5)
        self.volume_slider.grid(row=3, column=1, columnspan=2, padx=(10,10), pady=(10,10), sticky='ew')
        
    #-------------------------------------------Right Sidebar------------------------------------------
        self.right_frame = ctk.CTkFrame(self, width=int(self.width * 0.2))
        self.right_frame.grid(row=1, column=2, rowspan=3, sticky="nsew")

        self.live_emotion_label = ctk.CTkLabel(self.right_frame, text="Live Emotion", font=ctk.CTkFont(size=30), 
                                       text_color=("gray10", "#DCE4EE"), fg_color="#3B3B3B", corner_radius=5)
        self.live_emotion_label.grid(row=0, columnspan=2, padx=(20,20), pady=(20,10), sticky="new")
        self.live_emotions = ctk.CTkTextbox(self.right_frame, height=self.height*0.21, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))
        self.live_emotions.insert("end", "Please turn on webcam! This section will update every 5 seconds once it is started")
        self.live_emotions.grid(row=1, columnspan=2, padx=(20,20), sticky="nsew")

        self.emotion_label = ctk.CTkLabel(self.right_frame, text="Captured Emotion", font=ctk.CTkFont(size=30), 
                                       text_color=("gray10", "#DCE4EE"), fg_color="#3B3B3B", corner_radius=5)
        self.emotion_label.grid(row=2, columnspan=2, padx=(20,20), pady=(10,10), sticky="new")
        self.captured_emotions = ctk.CTkTextbox(self.right_frame, height=self.height*0.21, wrap="word", font=ctk.CTkFont(size=15), text_color=("gray10", "#DCE4EE"))
        self.captured_emotions.insert("end", "Start and stop the webcam to capture emotions!")
        self.captured_emotions.grid(row=3, columnspan=2, padx=(20,20), sticky="nsew")

        self.captured_img_label = ctk.CTkLabel(self.right_frame, text="Captured Image", font=ctk.CTkFont(size=30), 
                                       text_color=("gray10", "#DCE4EE"), fg_color="#3B3B3B", corner_radius=5)
        self.captured_img_label.grid(row=4, columnspan=2, padx=(20,20), pady=(10,0), sticky="new")
        self.captured_img = ctk.CTkLabel(self.right_frame, width=int(self.width * 0.20), height=int(self.height * 0.27), text="Nothing Captured Yet")
        self.captured_img.grid(row=5, columnspan=2, padx=(10, 10), pady=(0, 10), sticky='new')

    #---------------------------------------------Functions-------------------------------------------------
    def initialize_model(self):
        model = MusicGen.get_pretrained("facebook/musicgen-small")
        model.set_generation_params(duration=7) 
        return model

    def print_captured_emotions(self):
        self.captured_emotions.configure(state='normal')
        self.captured_emotions.delete('1.0', 'end')
        if self.success:
            for emotion, score in self.emotions.items():
                self.captured_emotions.insert("end", f"{emotion.capitalize()}: {score:.2f}%\n")
        else:
            self.self_emotions.insert("end", "No emotion detected. If Generate is clicked, it will retry automatically")
        self.captured_emotions.configure(state='disabled')

    def clear_live_emotions(self):
        self.live_emotions.configure(state='normal')
        self.live_emotions.delete('1.0', 'end')
        self.live_emotions.insert("end", "Please turn on webcam! This section will update every 5 seconds once it is started")
        self.live_emotions.configure(state='disabled')

    def genbutton_click(self):
        self.genbutton.configure(state="disabled")
        desc = self.prompt_entry.get()
        self.prompt_entry.configure(state='disabled')
        while not self.success:
            if self.cap:
                self.stop_webcam()
                self.success, self.emotions, self.prompt = ngf.capture_emotions(self.camera_frame)
            elif self.camera_frame is not None:
                self.success, self.emotions, self.prompt = ngf.capture_emotions(self.camera_frame)
            else:
                self.start_webcam()
                self.stop_webcam()
            self.camera_frame = None
        self.video_label.configure(image="", text="Music generating...! Please be patient while it generates.")
        music_path = ngf.generate_music(self.model, description=self.prompt + desc, index=len(self.music_path))
        self.success = 0
        self.music_path.append(music_path)
        self.genbutton.configure(state="normal")
        self.play_button.configure(state='normal')
        pa.play_audio(self.music_path[-1])
        self.set_volume(self.volume_slider.get())
        self.video_label.configure(text="Music generated! Please enjoy the music or turn on webcam to start again.")
        self.prompt_entry.configure(state='normal')

    def set_volume(self, vol):
        pa.volume_set(vol)

    def start_webcam(self):
        self.video_label.configure(text="")
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.cap = cv2.VideoCapture(0)
        self.update_frame()
        self.update_live_emotion() 

    def stop_webcam(self):
        if self.cap:
            _, self.camera_frame = self.cap.read()
            self.captured_image(self.camera_frame)
            self.cap.release()
            self.cap = None
            self.success, self.emotions, self.prompt = ngf.capture_emotions(self.camera_frame)
            if self.success:
                self.print_captured_emotions()
                self.clear_live_emotions()
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
    
    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, self.camera_frame = self.cap.read()
            if ret:
                img = cv2.cvtColor(self.camera_frame, cv2.COLOR_BGR2RGB)
                photo = Image.fromarray(img)
                photo_image = ImageTk.PhotoImage(image=photo)
                image_image = ImageTk.getimage(photo_image)
                ctk_image = ctk.CTkImage(image_image, size=((self.width * 0.50),int(self.height * 0.67)))
                self.video_label.configure(image=ctk_image)
                self.video_label.after(33, self.update_frame)  # Update every 33ms (30fps)

    def update_live_emotion(self):
        if self.cap and self.cap.isOpened():
            img = self.camera_frame
            success, emotions, _ = ngf.capture_emotions(img)
            self.live_emotions.configure(state='normal')
            self.live_emotions.delete('1.0', 'end')
            if success:
                for emotion, score in emotions.items():
                    self.live_emotions.insert("end", f"{emotion.capitalize()}: {score:.2f}%\n")
            else:
                self.live_emotions.insert("end", "No emotion detected, trying again")
            self.live_emotions.configure(state='disabled')
            self.live_emotions.after(5000, self.update_live_emotion) # Update every 5 seconds


    def captured_image(self, camera_frame):
            img = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
            photo = Image.fromarray(img)
            photo_image = ImageTk.PhotoImage(image=photo)
            image_image = ImageTk.getimage(photo_image)
            ctk_image = ctk.CTkImage(image_image, size=((self.width * 0.17),int(self.height * 0.23)))
            self.captured_img.configure(image=ctk_image, text="")

def on_closing(app):
    if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
        close_client()
        app.destroy()

    

if __name__ == "__main__":
    width, height, gui_size = get_display_size()
    app = App(width, height)
    app.geometry(gui_size)
    app.resizable(0, 0) #Non resizable window
    threading.Thread(target=run_client).start()
    app.protocol("WM_DELETE_WINDOW", lambda:on_closing(app))
    app.mainloop()
    
