import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
UPLOADS_DIR = BASE_DIR / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'crowd_monitor.db'}"

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Model Weights Paths
YOLO_PERSON_MODEL_PATH = str(MODELS_DIR / "yolov8n.pt")
YOLO_FIRE_SMOKE_MODEL_PATH = str(MODELS_DIR / "fire_smoke.pt")

# Inference Scheduling (Independent Intervals)
PERSON_INFERENCE_INTERVAL = 2       # Run person detection every 2 frames
FIRE_SMOKE_INFERENCE_INTERVAL = 5   # Run fire/smoke detection every 5 frames

# Default Monitoring Parameters
DEFAULT_SAFE_CAPACITY = 50

# Temporal Stabilization & Thresholds
FIRE_CONFIDENCE_THRESHOLD = 0.40
SMOKE_CONFIDENCE_THRESHOLD = 0.40
PERSON_CONFIDENCE_THRESHOLD = 0.35

FIRE_PERSISTENCE_FRAMES = 3
SMOKE_PERSISTENCE_FRAMES = 4
CROWD_PERSISTENCE_FRAMES = 3

# Hysteresis Thresholds for Crowd Levels (%)
# Upward transitions:
THRESH_MODERATE_UP = 50.0
THRESH_HIGH_UP = 75.0
THRESH_CRITICAL_UP = 90.0

# Downward transitions (hysteresis deadband prevents flickering):
THRESH_SAFE_DOWN = 46.0
THRESH_MODERATE_DOWN = 71.0
THRESH_HIGH_DOWN = 86.0

# Metric Persistence Rate (Seconds between DB writes)
METRIC_PERSIST_INTERVAL_SEC = 1.0

# Fire/Smoke Model Verification Info
VERIFIED_FIRE_SMOKE_MODEL_INFO = {
    "repo_id": "rabahdev/fire-smoke-yolov8n",
    "filename": "best.pt",
    "direct_url": "https://huggingface.co/rabahdev/fire-smoke-yolov8n/resolve/main/best.pt",
    "license": "AGPL-3.0 (Ultralytics compatible, open source)",
    "architecture": "YOLOv8n",
    "classes": {0: "smoke", 1: "fire"},
}
