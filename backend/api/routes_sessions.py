import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import MonitoringSession, CrowdMetric, EventLog
from ai.video_processor import session_manager

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

class ConfigUpdate(BaseModel):
    safe_capacity: Optional[int] = None

@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(MonitoringSession).filter(MonitoringSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()

@router.post("/{session_id}/start")
def start_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(MonitoringSession).filter(MonitoringSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if not os.path.exists(session.video_path):
        raise HTTPException(status_code=400, detail="Video file does not exist on disk")

    processor = session_manager.get_processor(session_id)
    if not processor:
        processor = session_manager.create_processor(
            session_id=session.id,
            video_path=session.video_path,
            safe_capacity=session.safe_capacity
        )
    processor.start()
    return {"status": "started", "session_id": session_id}

@router.post("/{session_id}/pause")
def pause_session(session_id: str):
    processor = session_manager.get_processor(session_id)
    if not processor:
        raise HTTPException(status_code=404, detail="Active processor not found")
    processor.pause()
    return {"status": "paused"}

@router.post("/{session_id}/resume")
def resume_session(session_id: str):
    processor = session_manager.get_processor(session_id)
    if not processor:
        raise HTTPException(status_code=404, detail="Active processor not found")
    processor.resume()
    return {"status": "resumed"}

@router.post("/{session_id}/stop")
def stop_session(session_id: str):
    processor = session_manager.get_processor(session_id)
    if processor:
        processor.stop()
    return {"status": "stopped"}

@router.get("/{session_id}/stream")
def stream_video(session_id: str, db: Session = Depends(get_db)):
    """MJPEG streaming endpoint for processed video frames."""
    processor = session_manager.get_processor(session_id)
    if not processor:
        session = db.query(MonitoringSession).filter(MonitoringSession.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        processor = session_manager.create_processor(
            session_id=session.id,
            video_path=session.video_path,
            safe_capacity=session.safe_capacity
        )
        processor.start()

    return StreamingResponse(
        processor.get_mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/{session_id}/metrics")
def get_session_metrics(session_id: str, db: Session = Depends(get_db)):
    metrics = db.query(CrowdMetric).filter(CrowdMetric.session_id == session_id).order_by(CrowdMetric.id.asc()).all()
    return [m.to_dict() for m in metrics]

@router.get("/{session_id}/events")
def get_session_events(session_id: str, db: Session = Depends(get_db)):
    events = db.query(EventLog).filter(EventLog.session_id == session_id).order_by(EventLog.id.desc()).all()
    return [e.to_dict() for e in events]

@router.patch("/{session_id}/config")
def update_session_config(session_id: str, config: ConfigUpdate, db: Session = Depends(get_db)):
    session = db.query(MonitoringSession).filter(MonitoringSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if config.safe_capacity is not None and config.safe_capacity > 0:
        session.safe_capacity = config.safe_capacity
        db.commit()
        processor = session_manager.get_processor(session_id)
        if processor:
            processor.update_config(safe_capacity=config.safe_capacity)

    return session.to_dict()
