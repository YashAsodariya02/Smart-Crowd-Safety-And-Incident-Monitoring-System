import logging
from typing import List, Dict, Any, Optional
import config
from ai.model_manager import Detection

logger = logging.getLogger("risk_engine")

class RiskEngine:
    def __init__(self, safe_capacity: int = config.DEFAULT_SAFE_CAPACITY):
        self.safe_capacity = safe_capacity
        self.current_crowd_level = "SAFE"
        
        # Temporal persistence counters (number of consecutive frames condition held)
        self.fire_consecutive_frames = 0
        self.smoke_consecutive_frames = 0
        self.high_crowd_consecutive_frames = 0
        self.critical_crowd_consecutive_frames = 0

        # Active incident tracking to prevent repeated spam
        self.active_incidents_by_type = {}  # e.g. {"FIRE": incident_id, "HIGH_CROWD": incident_id}

    def update_config(self, safe_capacity: Optional[int] = None):
        if safe_capacity is not None and safe_capacity > 0:
            self.safe_capacity = safe_capacity
            logger.info(f"Updated safe_capacity to {self.safe_capacity}")

    def calculate_crowd_level_with_hysteresis(self, occupancy: float) -> str:
        """
        Applies hysteresis deadbands to avoid rapid flickering near boundaries:
        Upward thresholds: 50% (MODERATE), 75% (HIGH), 90% (CRITICAL)
        Downward thresholds: 46% (SAFE), 71% (MODERATE), 86% (HIGH)
        """
        curr = self.current_crowd_level

        if curr == "SAFE":
            if occupancy >= config.THRESH_CRITICAL_UP:
                curr = "CRITICAL"
            elif occupancy >= config.THRESH_HIGH_UP:
                curr = "HIGH"
            elif occupancy >= config.THRESH_MODERATE_UP:
                curr = "MODERATE"
            else:
                curr = "SAFE"

        elif curr == "MODERATE":
            if occupancy >= config.THRESH_CRITICAL_UP:
                curr = "CRITICAL"
            elif occupancy >= config.THRESH_HIGH_UP:
                curr = "HIGH"
            elif occupancy < config.THRESH_SAFE_DOWN:
                curr = "SAFE"
            else:
                curr = "MODERATE"

        elif curr == "HIGH":
            if occupancy >= config.THRESH_CRITICAL_UP:
                curr = "CRITICAL"
            elif occupancy < config.THRESH_MODERATE_DOWN:
                curr = "MODERATE"
            elif occupancy < config.THRESH_SAFE_DOWN:
                curr = "SAFE"
            else:
                curr = "HIGH"

        elif curr == "CRITICAL":
            if occupancy < config.THRESH_HIGH_DOWN:
                curr = "HIGH"
            elif occupancy < config.THRESH_MODERATE_DOWN:
                curr = "MODERATE"
            elif occupancy < config.THRESH_SAFE_DOWN:
                curr = "SAFE"
            else:
                curr = "CRITICAL"

        self.current_crowd_level = curr
        return curr

    def evaluate_frame(
        self,
        timestamp_str: str,
        frame_idx: int,
        detections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluates frame perceptions and determines:
        - Person count & occupancy
        - Stabilized crowd level
        - Any new stabilized incidents (Fire, Smoke, Surge)
        """
        person_dets: List[Detection] = detections.get("person_detections", [])
        fire_smoke_dets: List[Detection] = detections.get("fire_smoke_detections", [])
        hazard_dets: List[Detection] = detections.get("hazard_detections", [])

        person_count = len(person_dets)
        occupancy = (person_count / max(1, self.safe_capacity)) * 100.0
        crowd_level = self.calculate_crowd_level_with_hysteresis(occupancy)

        # 1. Fire / Smoke evaluation
        fire_detected = False
        smoke_detected = False
        max_fire_conf = 0.0
        max_smoke_conf = 0.0

        for det in fire_smoke_dets:
            if det.class_name == "FIRE" and det.confidence >= config.FIRE_CONFIDENCE_THRESHOLD:
                fire_detected = True
                max_fire_conf = max(max_fire_conf, det.confidence)
            elif det.class_name == "SMOKE" and det.confidence >= config.SMOKE_CONFIDENCE_THRESHOLD:
                smoke_detected = True
                max_smoke_conf = max(max_smoke_conf, det.confidence)

        # Update persistence counters
        if fire_detected:
            self.fire_consecutive_frames += 1
        else:
            self.fire_consecutive_frames = max(0, self.fire_consecutive_frames - 1)

        if smoke_detected:
            self.smoke_consecutive_frames += 1
        else:
            self.smoke_consecutive_frames = max(0, self.smoke_consecutive_frames - 1)

        # Update crowd persistence
        if occupancy >= config.THRESH_CRITICAL_UP:
            self.critical_crowd_consecutive_frames += 1
            self.high_crowd_consecutive_frames += 1
        elif occupancy >= config.THRESH_HIGH_UP:
            self.high_crowd_consecutive_frames += 1
            self.critical_crowd_consecutive_frames = max(0, self.critical_crowd_consecutive_frames - 1)
        else:
            self.high_crowd_consecutive_frames = max(0, self.high_crowd_consecutive_frames - 1)
            self.critical_crowd_consecutive_frames = max(0, self.critical_crowd_consecutive_frames - 1)

        # Determine if new incidents should be created
        incidents_to_create = []

        # FIRE incident rule
        if self.fire_consecutive_frames >= config.FIRE_PERSISTENCE_FRAMES:
            if "FIRE" not in self.active_incidents_by_type:
                incidents_to_create.append({
                    "type": "FIRE",
                    "severity": "CRITICAL",
                    "confidence": max_fire_conf,
                    "timestamp": timestamp_str,
                    "details": f"Fire detected with {round(max_fire_conf * 100, 1)}% confidence, persisted for {self.fire_consecutive_frames} frames."
                })

        # SMOKE incident rule (or compound with fire)
        if self.smoke_consecutive_frames >= config.SMOKE_PERSISTENCE_FRAMES:
            if "SMOKE" not in self.active_incidents_by_type and "FIRE" not in self.active_incidents_by_type:
                severity = "CRITICAL" if fire_detected else "WARNING"
                incidents_to_create.append({
                    "type": "SMOKE",
                    "severity": severity,
                    "confidence": max_smoke_conf,
                    "timestamp": timestamp_str,
                    "details": f"Smoke hazard detected with {round(max_smoke_conf * 100, 1)}% confidence."
                })

        # CROWD OCCUPANCY incident rule
        if self.critical_crowd_consecutive_frames >= config.CROWD_PERSISTENCE_FRAMES:
            if "CRITICAL_CROWD" not in self.active_incidents_by_type:
                incidents_to_create.append({
                    "type": "CRITICAL_CROWD",
                    "severity": "CRITICAL",
                    "confidence": None,
                    "timestamp": timestamp_str,
                    "details": f"Critical crowd density exceeded {round(occupancy, 1)}% of safe capacity ({self.safe_capacity})."
                })
        elif self.high_crowd_consecutive_frames >= config.CROWD_PERSISTENCE_FRAMES:
            if "HIGH_CROWD" not in self.active_incidents_by_type and "CRITICAL_CROWD" not in self.active_incidents_by_type:
                incidents_to_create.append({
                    "type": "HIGH_CROWD",
                    "severity": "WARNING",
                    "confidence": None,
                    "timestamp": timestamp_str,
                    "details": f"High crowd occupancy detected: {round(occupancy, 1)}% ({person_count}/{self.safe_capacity} persons)."
                })

        # Count active hazards (fire + smoke + zone violations)
        hazards_count = (1 if fire_detected else 0) + (1 if smoke_detected else 0) + len(hazard_dets)

        # Average model confidence of current visible detections
        all_dets = detections.get("all_detections", [])
        if all_dets:
            avg_confidence = sum(d.confidence for d in all_dets) / len(all_dets)
        else:
            avg_confidence = 0.0

        return {
            "person_count": person_count,
            "occupancy": round(occupancy, 1),
            "crowd_level": crowd_level,
            "hazards_count": hazards_count,
            "avg_confidence": round(avg_confidence * 100, 1),
            "incidents_to_create": incidents_to_create,
            "fire_active": fire_detected,
            "smoke_active": smoke_detected,
        }

    def record_incident_opened(self, incident_type: str, incident_id: str):
        self.active_incidents_by_type[incident_type] = incident_id

    def record_incident_closed(self, incident_type: str):
        if incident_type in self.active_incidents_by_type:
            del self.active_incidents_by_type[incident_type]

    def reset(self):
        self.fire_consecutive_frames = 0
        self.smoke_consecutive_frames = 0
        self.high_crowd_consecutive_frames = 0
        self.critical_crowd_consecutive_frames = 0
        self.current_crowd_level = "SAFE"
        self.active_incidents_by_type.clear()
