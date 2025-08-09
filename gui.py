# src/gui.py
import tkinter as tk
from PIL import Image, ImageTk
import cv2
from compliment_mirror import ComplimentMirrorApp

class AppGUI:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.app = ComplimentMirrorApp()

        self.video_label = tk.Label(window)
        self.video_label.pack()

        button_frame = tk.Frame(window, bg="black")
        button_frame.pack(fill="x", expand=True, pady=10)

        self.btn_compliment = tk.Button(button_frame, text="New Compliment", command=self.app.trigger_new_compliments)
        self.btn_compliment.pack(side="left", expand=True, padx=5)

        self.btn_roast = tk.Button(button_frame, text="Toggle Roast Mode", command=self.toggle_roast)
        self.btn_roast.pack(side="left", expand=True, padx=5)
        
        self.delay = 15
        self.update()
        self.window.mainloop()

    def toggle_roast(self):
        self.app.roast_mode = not self.app.roast_mode
        mode_text = "Roast Mode" if self.app.roast_mode else "Compliment Mode"
        print(f"😈 Switched to {mode_text}")
        self.app.speak_text(mode_text)

    def update(self):
        frame = self.app.process_frame()
        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)
        self.window.after(self.delay, self.update)