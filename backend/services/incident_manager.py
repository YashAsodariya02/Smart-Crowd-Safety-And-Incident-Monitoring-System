import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from database.database import SessionLocal
from database.models import Incident, EventLog, MonitoringSession

logger = logging.getLogger("incident_manager")

class IncidentManager:
    def __init__(self):
        self._next_incident_num = 1
        self._init_counter()

    def _init_counter(self):
        try:
            db = SessionLocal()
            count = db.query(Incident).count()
            self._next_incident_num = count + 1
            db.close()
        except Exception:
            # DB table may not be initialized yet
            self._next_incident_num = 1

    def create_incident(
        self,
        session_id: str,
        incident_type: str,
        severity: str,
        confidence: Optional[float],
        timestamp: str,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and persists an incident and a corresponding event log."""
        db = SessionLocal()
        try:
            incident_id = f"INC-{self._next_incident_num:04d}"
            self._next_incident_num += 1

            new_incident = Incident(
                id=incident_id,
                session_id=session_id,
                type=incident_type,
                severity=severity,
                confidence=confidence,
                timestamp=timestamp,
                status="ACTIVE",
                details=details
            )
            db.add(new_incident)

            # Also create an EventLog entry
            event_type_name = incident_type.replace("_", " ")
            event_msg = f"{event_type_name} DETECTED"
            if confidence:
                event_msg += f" ({round(confidence * 100, 0):.0f}%)"
            
            event = EventLog(
                session_id=session_id,
                timestamp=timestamp,
                event_type=incident_type,
                message=event_msg,
                severity=severity
            )
            db.add(event)

            db.commit()
            db.refresh(new_incident)
            db.refresh(event)

            logger.info(f"Created incident {incident_id}: {incident_type} [{severity}] at {timestamp}")
            return {
                "incident": new_incident.to_dict(),
                "event": event.to_dict()
            }
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create incident: {e}")
            raise e
        finally:
            db.close()

    def acknowledge_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            inc = db.query(Incident).filter(Incident.id == incident_id).first()
            if not inc:
                return None
            inc.status = "ACKNOWLEDGED"

            event = EventLog(
                session_id=inc.session_id,
                timestamp=inc.timestamp,
                event_type="ACKNOWLEDGED",
                message=f"INCIDENT {incident_id} ACKNOWLEDGED BY OPERATOR",
                severity="INFO"
            )
            db.add(event)
            db.commit()
            db.refresh(inc)
            db.refresh(event)
            return {"incident": inc.to_dict(), "event": event.to_dict()}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to acknowledge incident {incident_id}: {e}")
            return None
        finally:
            db.close()

    def resolve_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        db = SessionLocal()
        try:
            inc = db.query(Incident).filter(Incident.id == incident_id).first()
            if not inc:
                return None
            inc.status = "RESOLVED"

            event = EventLog(
                session_id=inc.session_id,
                timestamp=inc.timestamp,
                event_type="RESOLVED",
                message=f"INCIDENT {incident_id} RESOLVED",
                severity="INFO"
            )
            db.add(event)
            db.commit()
            db.refresh(inc)
            db.refresh(event)
            return {"incident": inc.to_dict(), "event": event.to_dict()}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to resolve incident {incident_id}: {e}")
            return None
        finally:
            db.close()

    def add_event_log(self, session_id: str, timestamp: str, event_type: str, message: str, severity: str = "INFO") -> Dict[str, Any]:
        db = SessionLocal()
        try:
            event = EventLog(
                session_id=session_id,
                timestamp=timestamp,
                event_type=event_type,
                message=message,
                severity=severity
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event.to_dict()
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to add event log: {e}")
            return {}
        finally:
            db.close()

    def get_incidents_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            incidents = db.query(Incident).filter(Incident.session_id == session_id).order_by(Incident.created_at.desc()).all()
            return [i.to_dict() for i in incidents]
        finally:
            db.close()

    def get_events_for_session(self, session_id: str) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            events = db.query(EventLog).filter(EventLog.session_id == session_id).order_by(EventLog.created_at.desc()).all()
            return [e.to_dict() for e in events]
        finally:
            db.close()

incident_manager = IncidentManager()
