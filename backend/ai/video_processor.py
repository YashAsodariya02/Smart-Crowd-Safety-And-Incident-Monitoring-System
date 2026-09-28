import os
import cv2
import time
import math
import logging
import asyncio
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime

import config
from ai.model_manager import model_manager, Detection
from services.risk_engine import RiskEngine
from services.incident_manager import incident_manager
from database.database import SessionLocal
from database.models import MonitoringSession, CrowdMetric

logger = logging.getLogger("video_processor")

class VideoSessionProcessor:
    def __init__(self, session_id: str, video_path: str, safe_capacity: int = config.DEFAULT_SAFE_CAPACITY):
        self.session_id = session_id
        self.video_path = video_path
        self.safe_capacity = safe_capacity
        self.risk_engine = RiskEngine(safe_capacity=safe_capacity)

        self.is_running = False
        self.is_paused = False
        self.stop_requested = False

        self.current_frame_idx = 0
        self.total_frames = 0
        self.fps = 30.0
        self.duration = 0.0
        self.current_fps = 0.0
        self.peak_people = 0

        # Latest annotated frame buffer for MJPEG streaming
        self.latest_jpeg_frame: Optional[bytes] = None
        self.frame_lock = threading.Lock()
        self.new_frame_event = threading.Event()

        # Telemetry subscribers (WebSocket queues or callbacks)
        self.telemetry_listeners: List[asyncio.Queue] = []

        # Metric persistence rate tracking
        self.last_metric_persist_time = -1.0

        # Worker thread
        self.worker_thread: Optional[threading.Thread] = None

        self._probe_video()

    def _probe_video(self):
        """Reads video metadata using OpenCV."""
        cap = cv2.VideoCapture(self.video_path)
        if cap.isOpened():
            self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            if self.fps <= 0 or math.isnan(self.fps):
                self.fps = 30.0
            self.duration = self.total_frames / self.fps if self.fps > 0 else 0.0
            cap.release()
        logger.info(f"Probed video {self.video_path}: {self.total_frames} frames, {self.fps} FPS, {round(self.duration, 1)}s")

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self.stop_requested = False
        self.worker_thread = threading.Thread(target=self._run_processing_loop, daemon=True)
        self.worker_thread.start()
        logger.info(f"Started video processing thread for session {self.session_id}")

    def pause(self):
        self.is_paused = True
        logger.info(f"Paused video processing for session {self.session_id}")

    def resume(self):
        self.is_paused = False
        logger.info(f"Resumed video processing for session {self.session_id}")

    def stop(self):
        self.stop_requested = True
        self.is_running = False
        self.new_frame_event.set()
        logger.info(f"Stopped video processing for session {self.session_id}")

    def update_config(self, safe_capacity: Optional[int] = None):
        if safe_capacity is not None:
            self.safe_capacity = safe_capacity
            self.risk_engine.update_config(safe_capacity=safe_capacity)

    def register_telemetry_listener(self, queue: asyncio.Queue):
        if queue not in self.telemetry_listeners:
            self.telemetry_listeners.append(queue)

    def unregister_telemetry_listener(self, queue: asyncio.Queue):
        if queue in self.telemetry_listeners:
            self.telemetry_listeners.remove(queue)

    def _format_timestamp(self, seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"

    def _draw_hud_and_detections(self, frame, detections: List[Detection], frame_idx: int, fps: float, crowd_level: str):
        """Draws clean Neo-brutalist bounding boxes and status HUD."""
        h, w = frame.shape[:2]

        # 1. Draw detection boxes
        for det in detections:
            x1, y1, x2, y2 = det.box
            # Clip coordinates
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w - 1, x2), min(h - 1, y2)

            color = det.color
            # Border rectangle (thickness 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label badge
            label = f"{det.class_name} {int(det.confidence * 100)}%"
            (tw, th), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            
            # Badge background
            badge_y1 = max(0, y1 - th - 6)
            badge_y2 = y1
            cv2.rectangle(frame, (x1, badge_y1), (x1 + tw + 8, badge_y2), (20, 22, 26), -1)
            cv2.rectangle(frame, (x1, badge_y1), (x1 + tw + 8, badge_y2), color, 1)
            cv2.putText(frame, label, (x1 + 4, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)

        # 2. Bottom Telemetry Bar Overlay (surveillance style)
        bar_h = 32
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, h - bar_h), (w, h), (15, 17, 20), -1)
        cv2.addWeighted(overlay, 0.85, frame, 0.15, 0, frame)

        # Status text
        hud_left = f"YOLOv8n | {int(fps)} FPS | FRAME {frame_idx:05d} / {self.total_frames}"
        cv2.putText(frame, hud_left, (12, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1, cv2.LINE_AA)

        # AI Active Indicator
        ai_tag = "[ AI ACTIVE ]"
        cv2.putText(frame, ai_tag, (w - 130, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 91), 1, cv2.LINE_AA)

        # Level tag
        level_color = (0, 255, 91)
        if crowd_level == "MODERATE":
            level_color = (0, 230, 255)
        elif crowd_level == "HIGH":
            level_color = (59, 229, 255)
        elif crowd_level == "CRITICAL":
            level_color = (91, 0, 255)
            
        cv2.circle(frame, (w - 145, h - 15), 4, level_color, -1)

    def _persist_crowd_metric(self, timestamp_str: str, time_sec: float, frame_idx: int, person_count: int, occupancy: float, crowd_level: str):
        """Persists approximately one crowd metric sample per second into SQLite."""
        db = SessionLocal()
        try:
            metric = CrowdMetric(
                session_id=self.session_id,
                video_timestamp=timestamp_str,
                timestamp_sec=time_sec,
                frame_index=frame_idx,
                person_count=person_count,
                occupancy=occupancy,
                crowd_level=crowd_level
            )
            db.add(metric)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error persisting crowd metric: {e}")
        finally:
            db.close()

    def _update_session_status(self, status: str, peak: int):
        db = SessionLocal()
        try:
            s = db.query(MonitoringSession).filter(MonitoringSession.id == self.session_id).first()
            if s:
                s.status = status
                s.peak_people = peak
                db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating session status: {e}")
        finally:
            db.close()

    def _run_processing_loop(self):
        """Main processing thread loop reading video with OpenCV."""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {self.video_path}")
            self._update_session_status("ERROR", 0)
            self.is_running = False
            return

        self._update_session_status("PROCESSING", 0)
        incident_manager.add_event_log(
            self.session_id,
            "00:00",
            "MONITORING_START",
            "AI MONITORING INITIALIZED & STREAM STARTED",
            "INFO"
        )

        frame_interval_sec = 1.0 / max(1.0, self.fps)
        start_clock = time.time()
        fps_clock = time.time()
        fps_frame_count = 0

        try:
            while not self.stop_requested:
                if self.is_paused:
                    time.sleep(0.1)
                    continue

                loop_start = time.time()
                ret, frame = cap.read()
                if not ret:
                    # Video reached end -> loop for continuous monitoring viva demo, or complete
                    logger.info("Video reached end. Looping video for continuous viva monitoring demonstration.")
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    self.current_frame_idx = 0
                    continue

                self.current_frame_idx += 1
                video_time_sec = self.current_frame_idx / max(1.0, self.fps)
                timestamp_str = self._format_timestamp(video_time_sec)

                # FPS calculation
                fps_frame_count += 1
                if time.time() - fps_clock >= 1.0:
                    self.current_fps = fps_frame_count / (time.time() - fps_clock)
                    fps_frame_count = 0
                    fps_clock = time.time()

                # 1. Run YOLO inference via ModelManager (respecting independent intervals)
                detections_result = model_manager.process_frame(
                    frame=frame,
                    frame_idx=self.current_frame_idx,
                    person_interval=config.PERSON_INFERENCE_INTERVAL,
                    fire_smoke_interval=config.FIRE_SMOKE_INFERENCE_INTERVAL,
                )

                all_detections = detections_result["all_detections"]

                # 2. Evaluate via Risk Engine
                eval_result = self.risk_engine.evaluate_frame(
                    timestamp_str=timestamp_str,
                    frame_idx=self.current_frame_idx,
                    detections=detections_result
                )

                person_count = eval_result["person_count"]
                occupancy = eval_result["occupancy"]
                crowd_level = eval_result["crowd_level"]
                hazards_count = eval_result["hazards_count"]
                avg_conf = eval_result["avg_confidence"]

                if person_count > self.peak_people:
                    self.peak_people = person_count

                # 3. Trigger any new stabilized incidents
                for inc_info in eval_result["incidents_to_create"]:
                    try:
                        inc_data = incident_manager.create_incident(
                            session_id=self.session_id,
                            incident_type=inc_info["type"],
                            severity=inc_info["severity"],
                            confidence=inc_info["confidence"],
                            timestamp=inc_info["timestamp"],
                            details=inc_info["details"]
                        )
                        self.risk_engine.record_incident_opened(inc_info["type"], inc_data["incident"]["id"])
                        # Broadcast incident to listeners immediately
                        self._broadcast_telemetry({
                            "type": "incident_created",
                            "data": inc_data["incident"],
                            "event": inc_data["event"]
                        })
                    except Exception as e:
                        logger.error(f"Failed to record incident: {e}")

                # 4. Check CrowdMetric persistence (1 sample per second)
                if video_time_sec - self.last_metric_persist_time >= config.METRIC_PERSIST_INTERVAL_SEC:
                    self._persist_crowd_metric(
                        timestamp_str=timestamp_str,
                        time_sec=video_time_sec,
                        frame_idx=self.current_frame_idx,
                        person_count=person_count,
                        occupancy=occupancy,
                        crowd_level=crowd_level
                    )
                    self.last_metric_persist_time = video_time_sec

                # 5. Draw Annotations on Frame
                annotated_frame = frame.copy()
                self._draw_hud_and_detections(
                    frame=annotated_frame,
                    detections=all_detections,
                    frame_idx=self.current_frame_idx,
                    fps=self.current_fps if self.current_fps > 0 else self.fps,
                    crowd_level=crowd_level
                )

                # 6. Encode Frame to JPEG for MJPEG stream
                ret_enc, jpeg_buffer = cv2.imencode(".jpg", annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                if ret_enc:
                    with self.frame_lock:
                        self.latest_jpeg_frame = jpeg_buffer.tobytes()
                    self.new_frame_event.set()

                # 7. Broadcast Telemetry over WebSocket (lightweight JSON)
                telemetry_data = {
                    "type": "telemetry",
                    "session_id": self.session_id,
                    "frame_index": self.current_frame_idx,
                    "total_frames": self.total_frames,
                    "timestamp": timestamp_str,
                    "timestamp_sec": round(video_time_sec, 2),
                    "fps": round(self.current_fps if self.current_fps > 0 else self.fps, 1),
                    "person_count": person_count,
                    "peak_people": self.peak_people,
                    "safe_capacity": self.safe_capacity,
                    "occupancy": occupancy,
                    "crowd_level": crowd_level,
                    "hazards_count": hazards_count,
                    "avg_confidence": avg_conf,
                    "models_status": {
                        "person_model": model_manager.person_model_status,
                        "fire_smoke_model": model_manager.fire_smoke_model_status,
                    }
                }
                self._broadcast_telemetry(telemetry_data)

                # Frame pacing: sleep remaining time in frame budget to preserve normal speed
                elapsed = time.time() - loop_start
                sleep_time = max(0.005, frame_interval_sec - elapsed)
                time.sleep(sleep_time)

        except Exception as e:
            logger.error(f"Unhandled error in video processing loop: {e}", exc_info=True)
            self._update_session_status("ERROR", self.peak_people)
        finally:
            cap.release()
            self.is_running = False
            self._update_session_status("COMPLETED", self.peak_people)
            logger.info(f"Video processing loop terminated for session {self.session_id}")

    def _broadcast_telemetry(self, message: Dict[str, Any]):
        """Pushes telemetry messages to any active WebSocket queues."""
        for queue in list(self.telemetry_listeners):
            try:
                queue.put_nowait(message)
            except Exception:
                pass

    def get_mjpeg_generator(self):
        """Generator yielding MJPEG multipart frames for HTTP streaming."""
        while self.is_running and not self.stop_requested:
            if self.new_frame_event.wait(timeout=1.0):
                self.new_frame_event.clear()
                with self.frame_lock:
                    frame_bytes = self.latest_jpeg_frame

                if frame_bytes:
                    yield (
                        b"--frame\r\n"
                        b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
                    )
            else:
                # If paused or waiting
                time.sleep(0.05)


class SessionManager:
    """Manages active video processing sessions."""
    def __init__(self):
        self.processors: Dict[str, VideoSessionProcessor] = {}

    def create_processor(self, session_id: str, video_path: str, safe_capacity: int = config.DEFAULT_SAFE_CAPACITY) -> VideoSessionProcessor:
        if session_id in self.processors:
            self.processors[session_id].stop()
        processor = VideoSessionProcessor(session_id, video_path, safe_capacity)
        self.processors[session_id] = processor
        return processor

    def get_processor(self, session_id: str) -> Optional[VideoSessionProcessor]:
        return self.processors.get(session_id)

    def stop_all(self):
        for p in self.processors.values():
            p.stop()
        self.processors.clear()

session_manager = SessionManager()
