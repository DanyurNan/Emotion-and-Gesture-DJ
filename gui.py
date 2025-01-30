import tkinter as tk
import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from functools import partial


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

    #Window
        self.title("EECS 159")
        self.width = width
        self.height = height
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((0,2), weight=0)
        self.grid_rowconfigure((1, 2), weight=1)
        
        self.set_label = ctk.CTkLabel(self, text="Settings", font=ctk.CTkFont(size=40, weight="bold"))
        self.set_label.grid(row=0, column=2, pady=(20,10))
    #Left Sidebar
        self.gesture_label = ctk.CTkLabel(self, text="Gestures", font=ctk.CTkFont(size=40, weight="bold"))
        self.gesture_label.grid(row=0, column=0, pady=(20,10))
        self.left_frame = ctk.CTkScrollableFrame(self, width=int(self.width * 0.2), label_text="New Gestures +")

        self.left_frame._label.bind("<Button-1>", self.newButton)
        self.left_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
        self.left_frame.grid_columnconfigure(0, weight=1)
        self.left_frame_button_width=int(self.width*0.2)

        self.gesture_list = [] 

    #Middle
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=1, rowspan=3, padx=(20,20), sticky='nsew')
        self.tabs.add("Audiocraft")
        self.tabs.add("Camera")
        self.tabs.add("Settings")
        self.tabs._segmented_button.configure(border_width=5, corner_radius=10,font=ctk.CTkFont(size=40, weight="bold"))
        #Audiocraft
        self.prompt = ctk.CTkEntry(self.tabs.tab("Audiocraft"), width=int(self.width * 0.4), placeholder_text="Music Prompt (Optional)")
        self.prompt.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.genbutton = ctk.CTkButton(self.tabs.tab("Audiocraft"), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.genbutton.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        #Camera
        self.video_label = ctk.CTkLabel(self.tabs.tab("Camera"), width=int(self.width * 0.52), height=int(self.height * 0.7), text="Webcam Feed")
        self.video_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.start_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Start Webcam", command=self.start_webcam)
        self.start_button.grid(row=1, column=0, padx=10, pady=15)

        self.stop_button = ctk.CTkButton(self.tabs.tab("Camera"), text="Stop Webcam", command=self.stop_webcam, state="disabled")
        self.stop_button.grid(row=1, column=1, padx=10, pady=15)

        self.cap = cv2.VideoCapture(0)  # 0 for default camera
        
    #Right Sidebar 
        self.right_frame = ctk.CTkFrame(self, width=int(self.width * 0.2))
        self.right_frame.grid(row=1, column=2, rowspan=3, sticky="nsew")

    #Functions
    def newButton(self, event): #Might be replaced
        i = len(self.gesture_list)
        self.gesture_list.append(ctk.CTkButton(self.left_frame, text=f'Gesture {i + 1}', font=ctk.CTkFont(size=30),
                                 width=self.left_frame_button_width, border_width=2, fg_color="transparent", text_color=("gray10", "#DCE4EE")))
        self.gesture_list[i].grid(row=i+1, column=0, padx=(10,10), pady=(0, 10))
        self.gesture_list[i].configure(command=partial(self.button_click, self.gesture_list[i]))

    def button_click(self, button): #Changes button color when clicked
        button.configure(fg_color="gray30")
        
    def start_webcam(self):
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.update_frame()

    def stop_webcam(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")

    def update_frame(self):
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = Image.fromarray(img)
                photo_image = ImageTk.PhotoImage(image=photo)
                image_image = ImageTk.getimage(photo_image)
                ctk_image = ctk.CTkImage(image_image, size=((self.width * 0.52),int(self.height * 0.7)))
                self.video_label.configure(image=ctk_image)
                self.video_label.after(15, self.update_frame)  # Update every 15ms

width, height, gui_size = get_display_size()
app = App(width, height)
app.geometry(gui_size)
app.resizable(0, 0) #Non resizable window
app.mainloop()
