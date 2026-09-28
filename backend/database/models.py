from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class MonitoringSession(Base):
    __tablename__ = "monitoring_sessions"

    id = Column(String(64), primary_key=True, index=True)
    video_name = Column(String(255), nullable=False)
    video_path = Column(String(512), nullable=False)
    duration = Column(Float, default=0.0)
    total_frames = Column(Integer, default=0)
    fps = Column(Float, default=30.0)
    status = Column(String(32), default="UPLOADED") # UPLOADED, PROCESSING, PAUSED, COMPLETED, ERROR
    peak_people = Column(Integer, default=0)
    safe_capacity = Column(Integer, default=50)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    incidents = relationship("Incident", back_populates="session", cascade="all, delete-orphan")
    metrics = relationship("CrowdMetric", back_populates="session", cascade="all, delete-orphan")
    event_logs = relationship("EventLog", back_populates="session", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "video_name": self.video_name,
            "video_path": self.video_path,
            "duration": round(self.duration, 2),
            "total_frames": self.total_frames,
            "fps": round(self.fps, 2),
            "status": self.status,
            "peak_people": self.peak_people,
            "safe_capacity": self.safe_capacity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(32), primary_key=True, index=True) # e.g. INC-0001
    session_id = Column(String(64), ForeignKey("monitoring_sessions.id"), nullable=False)
    type = Column(String(64), nullable=False) # FIRE, SMOKE, HIGH_CROWD, CRITICAL_CROWD, RESTRICTED_ZONE
    severity = Column(String(32), nullable=False) # CRITICAL, WARNING, INFO
    confidence = Column(Float, nullable=True)
    timestamp = Column(String(32), nullable=False) # e.g. "00:43"
    status = Column(String(32), default="ACTIVE") # ACTIVE, ACKNOWLEDGED, RESOLVED
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("MonitoringSession", back_populates="incidents")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "type": self.type,
            "severity": self.severity,
            "confidence": round(self.confidence * 100, 1) if self.confidence else None,
            "timestamp": self.timestamp,
            "status": self.status,
            "details": self.details,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class CrowdMetric(Base):
    __tablename__ = "crowd_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    video_timestamp = Column(String(32), nullable=False) # e.g. "00:15"
    timestamp_sec = Column(Float, default=0.0)
    frame_index = Column(Integer, default=0)
    person_count = Column(Integer, default=0)
    occupancy = Column(Float, default=0.0)
    crowd_level = Column(String(32), default="SAFE")
    created_at = Column(DateTime, default=utc_now)

    session = relationship("MonitoringSession", back_populates="metrics")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "video_timestamp": self.video_timestamp,
            "timestamp_sec": round(self.timestamp_sec, 2),
            "frame_index": self.frame_index,
            "person_count": self.person_count,
            "occupancy": round(self.occupancy, 1),
            "crowd_level": self.crowd_level
        }

class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("monitoring_sessions.id"), nullable=False, index=True)
    timestamp = Column(String(32), nullable=False) # e.g. "01:21"
    event_type = Column(String(64), nullable=False)
    message = Column(String(255), nullable=False)
    severity = Column(String(32), default="INFO")
    created_at = Column(DateTime, default=utc_now)

    session = relationship("MonitoringSession", back_populates="event_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "message": self.message,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
