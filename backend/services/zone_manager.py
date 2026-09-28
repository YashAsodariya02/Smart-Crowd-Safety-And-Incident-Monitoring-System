import cv2
import numpy as np
from typing import List, Dict, Any, Optional

class Zone:
    def __init__(self, zone_id: str, name: str, polygon: List[List[int]], zone_type: str = "RESTRICTED"):
        self.zone_id = zone_id
        self.name = name
        self.polygon = np.array(polygon, dtype=np.int32)
        self.zone_type = zone_type # RESTRICTED or COUNTING
        self.active_occupants = 0

    def contains_point(self, pt: tuple) -> bool:
        # cv2.pointPolygonTest returns > 0 if inside, 0 on edge, < 0 outside
        return cv2.pointPolygonTest(self.polygon, (float(pt[0]), float(pt[1])), False) >= 0

    def check_bbox_intrusion(self, bbox: List[int]) -> bool:
        # Check if bottom-center of bounding box (footpoint) is inside polygon
        x1, y1, x2, y2 = bbox
        foot_pt = ((x1 + x2) // 2, y2)
        return self.contains_point(foot_pt)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "polygon": self.polygon.tolist(),
            "zone_type": self.zone_type,
            "active_occupants": self.active_occupants
        }

class ZoneManager:
    """
    Future-ready ZoneManager for polygon-based spatial analysis
    and restricted zone intrusion detection.
    """
    def __init__(self):
        self.zones: Dict[str, Zone] = {}

    def add_zone(self, zone_id: str, name: str, polygon: List[List[int]], zone_type: str = "RESTRICTED") -> Zone:
        zone = Zone(zone_id, name, polygon, zone_type)
        self.zones[zone_id] = zone
        return zone

    def remove_zone(self, zone_id: str) -> bool:
        if zone_id in self.zones:
            del self.zones[zone_id]
            return True
        return False

    def get_all_zones(self) -> List[Dict[str, Any]]:
        return [z.to_dict() for z in self.zones.values()]

    def evaluate_detections(self, person_bboxes: List[List[int]]) -> Dict[str, Any]:
        """
        Evaluates person footpoints against all registered zones.
        Returns active violations and zone counts.
        """
        violations = []
        zone_counts = {}

        for zone_id, zone in self.zones.items():
            occupants = 0
            for bbox in person_bboxes:
                if zone.check_bbox_intrusion(bbox):
                    occupants += 1
            
            zone.active_occupants = occupants
            zone_counts[zone_id] = occupants

            if zone.zone_type == "RESTRICTED" and occupants > 0:
                violations.append({
                    "zone_id": zone_id,
                    "zone_name": zone.name,
                    "occupants": occupants,
                    "type": "RESTRICTED_ZONE_ENTRY",
                    "severity": "WARNING"
                })

        return {
            "violations": violations,
            "zone_counts": zone_counts
        }

    def draw_zones(self, frame):
        """Draws zone boundaries on the video frame."""
        for zone in self.zones.values():
            color = (0, 0, 255) if zone.zone_type == "RESTRICTED" else (255, 200, 0)
            cv2.polylines(frame, [zone.polygon], isClosed=True, color=color, thickness=2)
            # Label
            x, y = zone.polygon[0]
            label = f"{zone.name}: {zone.active_occupants}"
            cv2.putText(frame, label, (int(x), int(y) - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

zone_manager = ZoneManager()
