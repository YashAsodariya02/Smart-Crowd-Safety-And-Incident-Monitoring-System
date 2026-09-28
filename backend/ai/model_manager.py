import os
import urllib.request
import logging
from typing import List, Dict, Any, Optional
from ultralytics import YOLO
import config

logger = logging.getLogger("model_manager")
logging.basicConfig(level=logging.INFO)

class Detection:
    def __init__(self, box: List[int], class_name: str, confidence: float, color: tuple):
        self.box = box  # [x1, y1, x2, y2]
        self.class_name = class_name
        self.confidence = confidence
        self.color = color  # BGR format for OpenCV

    def to_dict(self) -> Dict[str, Any]:
        return {
            "box": self.box,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 3),
        }

class ModelManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.person_model: Optional[YOLO] = None
        self.fire_smoke_model: Optional[YOLO] = None
        self.hazard_model: Optional[YOLO] = None

        self.person_model_status = "UNINITIALIZED"
        self.fire_smoke_model_status = "NOT INSTALLED"
        self.hazard_model_status = "NOT CONFIGURED"

        # Cached detections between inference intervals
        self.cached_person_detections: List[Detection] = []
        self.cached_fire_smoke_detections: List[Detection] = []
        self.cached_hazard_detections: List[Detection] = []

        self.last_person_inference_frame = -1
        self.last_fire_smoke_inference_frame = -1

        self._initialized = True
        self.initialize_models()

    def initialize_models(self):
        """Loads available YOLO models once."""
        # 1. Load Person Model (COCO YOLOv8n)
        try:
            if not os.path.exists(config.YOLO_PERSON_MODEL_PATH):
                logger.info(f"Downloading baseline YOLOv8n to {config.YOLO_PERSON_MODEL_PATH}...")
                self.person_model = YOLO("yolov8n.pt")
                # Save into backend/models if needed
            else:
                self.person_model = YOLO(config.YOLO_PERSON_MODEL_PATH)
            
            self.person_model_status = "ACTIVE"
            logger.info("YOLOv8 Person Model successfully loaded: ACTIVE")
        except Exception as e:
            logger.error(f"Failed to load person model: {e}")
            self.person_model_status = f"ERROR: {e}"

        # 2. Load Fire / Smoke Model (Failsafe check)
        self.reload_fire_smoke_model()

        # Warm up models so first user frame does not lag
        self._warmup_models()

    def _warmup_models(self):
        """Runs a 1-frame dummy inference to warm up PyTorch CPU kernels."""
        import numpy as np
        dummy = np.zeros((320, 320, 3), dtype=np.uint8)
        try:
            if self.person_model:
                self.person_model.predict(source=dummy, classes=[0], imgsz=384, verbose=False, device="cpu")
            if self.fire_smoke_model:
                self.fire_smoke_model.predict(source=dummy, imgsz=384, verbose=False, device="cpu")
            logger.info("YOLO models warmed up successfully.")
        except Exception as e:
            logger.warning(f"Model warmup warning: {e}")

    def reload_fire_smoke_model(self):
        """Checks for fire_smoke.pt and loads it if present, without failing the app."""
        if os.path.exists(config.YOLO_FIRE_SMOKE_MODEL_PATH):
            try:
                self.fire_smoke_model = YOLO(config.YOLO_FIRE_SMOKE_MODEL_PATH)
                self.fire_smoke_model_status = "ACTIVE"
                logger.info(f"Fire/Smoke Model successfully loaded from {config.YOLO_FIRE_SMOKE_MODEL_PATH}: ACTIVE")
            except Exception as e:
                logger.error(f"Error loading fire_smoke.pt: {e}")
                self.fire_smoke_model_status = f"ERROR: {e}"
        else:
            self.fire_smoke_model = None
            self.fire_smoke_model_status = "NOT INSTALLED"
            logger.warning(f"Fire/Smoke model not found at {config.YOLO_FIRE_SMOKE_MODEL_PATH}. Running in failsafe mode.")

    def download_verified_fire_smoke_model(self) -> bool:
        """Downloads the verified AGPL-3.0 YOLOv8 fire/smoke weights from Hugging Face."""
        url = config.VERIFIED_FIRE_SMOKE_MODEL_INFO["direct_url"]
        target_path = config.YOLO_FIRE_SMOKE_MODEL_PATH
        logger.info(f"Downloading verified fire/smoke model from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp, open(target_path, "wb") as f:
                f.write(resp.read())
            logger.info("Download completed successfully.")
            self.reload_fire_smoke_model()
            return True
        except Exception as e:
            logger.error(f"Failed to download fire/smoke model: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """Returns the health and readiness of all models."""
        return {
            "person_model": {
                "name": "YOLOv8n (COCO)",
                "status": self.person_model_status,
                "classes": ["person"],
                "interval_frames": config.PERSON_INFERENCE_INTERVAL,
            },
            "fire_smoke_model": {
                "name": "YOLOv8n Fire/Smoke (D-Fire)",
                "status": self.fire_smoke_model_status,
                "classes": ["fire", "smoke"] if self.fire_smoke_model else [],
                "interval_frames": config.FIRE_SMOKE_INFERENCE_INTERVAL,
                "verification_info": config.VERIFIED_FIRE_SMOKE_MODEL_INFO
            },
            "hazard_model": {
                "name": "Hazard Extension Model",
                "status": self.hazard_model_status,
                "classes": []
            }
        }

    def process_frame(
        self,
        frame,
        frame_idx: int,
        person_interval: int = config.PERSON_INFERENCE_INTERVAL,
        fire_smoke_interval: int = config.FIRE_SMOKE_INFERENCE_INTERVAL,
        person_conf_thresh: float = config.PERSON_CONFIDENCE_THRESHOLD,
        fire_conf_thresh: float = config.FIRE_CONFIDENCE_THRESHOLD,
        smoke_conf_thresh: float = config.SMOKE_CONFIDENCE_THRESHOLD,
    ) -> Dict[str, Any]:
        """
        Runs inference on the frame respecting independent intervals and caches results.
        Returns:
            {
                "person_detections": List[Detection],
                "fire_smoke_detections": List[Detection],
                "hazard_detections": List[Detection],
                "all_detections": List[Detection],
                "person_inferred": bool,
                "fire_smoke_inferred": bool
            }
        """
        person_inferred = False
        fire_smoke_inferred = False

        # 1. Person Detection Inference (every N frames)
        if self.person_model and (frame_idx % person_interval == 0 or self.last_person_inference_frame < 0):
            try:
                # Class 0 is 'person' in COCO YOLOv8
                results = self.person_model.predict(
                    source=frame,
                    classes=[0],
                    conf=person_conf_thresh,
                    imgsz=416,
                    verbose=False,
                    device="cpu"
                )
                new_person_dets = []
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        coords = [int(v) for v in box.xyxy[0].tolist()]
                        conf = float(box.conf[0])
                        # Person border: Neo-brutalist Blue #2D27FF -> BGR (255, 39, 45)
                        new_person_dets.append(
                            Detection(coords, "PERSON", conf, (255, 39, 45))
                        )
                self.cached_person_detections = new_person_dets
                self.last_person_inference_frame = frame_idx
                person_inferred = True
            except Exception as e:
                logger.error(f"Error in person inference at frame {frame_idx}: {e}")

        # 2. Fire & Smoke Inference (every M frames, if installed)
        if self.fire_smoke_model and (frame_idx % fire_smoke_interval == 0 or self.last_fire_smoke_inference_frame < 0):
            try:
                results = self.fire_smoke_model.predict(
                    source=frame,
                    conf=min(fire_conf_thresh, smoke_conf_thresh),
                    imgsz=416,
                    verbose=False,
                    device="cpu"
                )
                new_fire_smoke_dets = []
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    names = results[0].names  # e.g. {0: 'smoke', 1: 'fire'}
                    for box in boxes:
                        cls_id = int(box.cls[0])
                        cls_name = names.get(cls_id, "").lower()
                        conf = float(box.conf[0])
                        coords = [int(v) for v in box.xyxy[0].tolist()]

                        if "fire" in cls_name and conf >= fire_conf_thresh:
                            # Fire: Neo-brutalist Critical #FF005B -> BGR (91, 0, 255)
                            new_fire_smoke_dets.append(
                                Detection(coords, "FIRE", conf, (91, 0, 255))
                            )
                        elif "smoke" in cls_name and conf >= smoke_conf_thresh:
                            # Smoke: Neo-brutalist Warning #FFE53B -> BGR (59, 229, 255)
                            new_fire_smoke_dets.append(
                                Detection(coords, "SMOKE", conf, (59, 229, 255))
                            )
                self.cached_fire_smoke_detections = new_fire_smoke_dets
                self.last_fire_smoke_inference_frame = frame_idx
                fire_smoke_inferred = True
            except Exception as e:
                logger.error(f"Error in fire/smoke inference at frame {frame_idx}: {e}")

        all_detections = self.cached_person_detections + self.cached_fire_smoke_detections + self.cached_hazard_detections

        return {
            "person_detections": self.cached_person_detections,
            "fire_smoke_detections": self.cached_fire_smoke_detections,
            "hazard_detections": self.cached_hazard_detections,
            "all_detections": all_detections,
            "person_inferred": person_inferred,
            "fire_smoke_inferred": fire_smoke_inferred
        }

    def reset_cache(self):
        """Clears cached detections between video sessions."""
        self.cached_person_detections = []
        self.cached_fire_smoke_detections = []
        self.cached_hazard_detections = []
        self.last_person_inference_frame = -1
        self.last_fire_smoke_inference_frame = -1

# Singleton access
model_manager = ModelManager()
