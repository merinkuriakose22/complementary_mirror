import cv2
import pyttsx3
import time
import math
import queue
import threading

import config
from ai_compliments import get_ai_response
from voice_control import VoiceController
from analyzer import get_face_attributes

class ComplimentMirrorApp:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(config.HAARCASCADE_FACE_PATH)
        self.engine = pyttsx3.init()
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        
        self.tracked_faces = {}
        self.next_face_id = 0
        self.frame_count = 0
        self.face_colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
        
        self.voice_controller = VoiceController()
        self.roast_mode = False
        self.tts_lock = threading.Lock()
        
        self.frame = None # To store the current frame for access by other methods
        
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        
        self.voice_controller.start()
        print("✨ Compliment Chaos Mirror Initialized ✨")

    def speak_text(self, text):
        if config.ENABLE_VOICE and self.engine:
            def speak():
                with self.tts_lock:
                    self.engine.say(text)
                    self.engine.runAndWait()
            threading.Thread(target=speak, daemon=True).start()

    def _process_new_face_in_background(self, face_id, face_roi):
        response_text = get_ai_response(self.roast_mode)
        if face_id in self.tracked_faces:
            self.tracked_faces[face_id]["compliment"] = response_text
            self.tracked_faces[face_id]["animation_start"] = time.time()
        self.speak_text(response_text)

    def trigger_new_compliments(self):
        """
        Gets new compliments for all visible faces. This method is called by the GUI button.
        """
        if not self.frame: # Don't do anything if there's no frame yet
            return
            
        print("💬 Getting new AI responses for everyone...")
        frame_copy = self.frame.copy() # Use a copy to avoid race conditions
        
        for face_id, face_info in self.tracked_faces.items():
            (x,y,w,h) = face_info["last_position"]
            face_roi = frame_copy[y:y+h, x:x+w]
            threading.Thread(target=self._process_new_face_in_background, args=(face_id, face_roi), daemon=True).start()

    def find_matching_face(self, new_face_rect):
        for face_id, face_info in self.tracked_faces.items():
            if self.calculate_distance(new_face_rect, face_info["last_position"]) < config.DISTANCE_THRESHOLD:
                return face_id
        return None

    def calculate_distance(self, face1, face2):
        x1, y1, w1, h1 = face1; x2, y2, w2, h2 = face2
        return math.sqrt((x1 + w1//2 - (x2 + w2//2))**2 + (y1 + h1//2 - (y2 + h2//2))**2)

    def draw_animated_text(self, frame, face_info, position, current_time):
        x, y = position; text = face_info.get("compliment", "")
        if "animation_start" not in face_info: face_info.update({"animation_start": current_time, "animated_length": 0})
        elapsed = current_time - face_info["animation_start"]
        target_length = min(len(text), int(elapsed / config.TYPING_SPEED))
        if face_info.get("animated_length", 0) < target_length: face_info["animated_length"] = target_length
        animated_text = text[:face_info["animated_length"]]
        cursor = "|" if int(current_time * 2) % 2 == 0 and face_info["animated_length"] < len(text) else ""
        font = cv2.FONT_HERSHEY_SIMPLEX
        (text_w, text_h), _ = cv2.getTextSize(animated_text + cursor, font, 0.6, 2)
        box_x, box_y = x, y - 40
        cv2.rectangle(frame, (box_x - 5, box_y - 25), (box_x + text_w + 5, y + 10), (20, 20, 20), -1)
        cv2.putText(frame, animated_text + cursor, (box_x, y), font, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret: return None

        self.frame = cv2.flip(frame, 1) # Store the flipped frame as an instance attribute
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        current_time = time.time()

        try:
            command = self.voice_controller.command_queue.get_nowait()
            if command == "change_compliment": self.trigger_new_compliments()
        except queue.Empty: pass
        
        if self.frame_count % config.FACE_DETECTION_INTERVAL == 0:
            detected_faces = self.face_cascade.detectMultiScale(
                gray, config.FACE_SCALE_FACTOR, config.FACE_MIN_NEIGHBORS, minSize=config.FACE_MIN_SIZE
            )
            for (x, y, w, h) in detected_faces:
                matched_id = self.find_matching_face((x,y,w,h))
                if matched_id:
                    self.tracked_faces[matched_id]['last_seen'] = current_time
                elif len(self.tracked_faces) < 3:
                    face_id = f"Person_{self.next_face_id}"
                    self.next_face_id += 1
                    self.tracked_faces[face_id] = {
                        "last_position": (x,y,w,h), "last_seen": current_time,
                        "compliment": "Thinking...", "color": self.face_colors[self.next_face_id % len(self.face_colors)]
                    }
                    face_roi = self.frame[y:y+h, x:x+w]
                    threading.Thread(target=self._process_new_face_in_background, args=(face_id, face_roi), daemon=True).start()

        for face_id, face_info in list(self.tracked_faces.items()):
            if current_time - face_info.get("last_seen", 0) > config.FACE_TIMEOUT:
                del self.tracked_faces[face_id]
            else:
                (x,y,w,h) = face_info["last_position"]
                self.tracked_faces[face_id]['last_position'] = (x,y,w,h)
                color = face_info["color"]
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(self.frame, face_id, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                self.draw_animated_text(self.frame, face_info, (x,y), current_time)
        
        self.frame_count += 1
        return self.frame