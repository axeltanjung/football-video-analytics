import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_DIR = BASE_DIR / "models"

UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
MODEL_DIR.mkdir(exist_ok=True)

YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
YOLO_CONFIDENCE_THRESHOLD = float(os.getenv("YOLO_CONFIDENCE", "0.4"))
YOLO_IOU_THRESHOLD = float(os.getenv("YOLO_IOU", "0.5"))

DEEPSORT_MAX_AGE = int(os.getenv("DEEPSORT_MAX_AGE", "30"))
DEEPSORT_N_INIT = int(os.getenv("DEEPSORT_N_INIT", "3"))
DEEPSORT_MAX_COSINE_DISTANCE = float(os.getenv("DEEPSORT_MAX_COSINE_DIST", "0.3"))

FRAME_SKIP = int(os.getenv("FRAME_SKIP", "2"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "8"))

PITCH_LENGTH_M = 105.0
PITCH_WIDTH_M = 68.0

GOAL_AREA_X_THRESHOLD = 0.85
SHOT_VELOCITY_THRESHOLD = 15.0
PASS_PROXIMITY_THRESHOLD = 50.0
POSSESSION_RADIUS_PX = 80.0

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{BASE_DIR / 'football_analytics.db'}")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
