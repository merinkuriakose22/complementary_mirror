import os
import cv2

# --- AI Model Configuration ---
# ✅ Groq model to use
AI_MODEL_NAME = "llama-3.3-70b-versatile"

# 🔑 IMPORTANT: Replace this with your Groq API key or set it as an environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")

# --- Path Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
COMPLIMENTS_DIR = os.path.join(ASSETS_DIR, 'compliments')
FALLBACK_COMPLIMENTS_PATH = os.path.join(COMPLIMENTS_DIR, 'general.txt')
HAARCASCADE_FACE_PATH = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')

# --- Feature Flags ---
ENABLE_AI = True
ENABLE_VOICE = True

# --- Camera & Other Settings ---
CAMERA_INDEX = 0
CAMERA_WIDTH = 800
CAMERA_HEIGHT = 600
TYPING_SPEED = 0.05
FACE_DETECTION_INTERVAL = 20
FACE_TIMEOUT = 5.0
DISTANCE_THRESHOLD = 90
FACE_SCALE_FACTOR = 1.2
FACE_MIN_NEIGHBORS = 6
FACE_MIN_SIZE = (90, 90)
