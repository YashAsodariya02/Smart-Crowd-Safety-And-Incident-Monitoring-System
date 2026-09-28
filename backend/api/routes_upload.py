import os
import uuid
import math
import cv2
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import config
from database.database import get_db
from database.models import MonitoringSession

router = APIRouter(prefix="/api/videos", tags=["Videos"])

def probe_video_metadata(video_path: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0, 30.0, 0.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    if fps <= 0 or math.isnan(fps):
        fps = 30.0
    duration = total_frames / fps if fps > 0 else 0.0
    cap.release()
    return total_frames, fps, duration

@router.post("/upload")
async def upload_video(
    file: UploadFile = File(...),
    safe_capacity: int = Form(config.DEFAULT_SAFE_CAPACITY),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: MP4, AVI, MOV, MKV")

    session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
    filename = f"{session_id}_{file.filename}"
    file_path = os.path.join(config.UPLOADS_DIR, filename)

    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

    total_frames, fps, duration = probe_video_metadata(file_path)

    session = MonitoringSession(
        id=session_id,
        video_name=file.filename,
        video_path=file_path,
        duration=duration,
        total_frames=total_frames,
        fps=fps,
        status="UPLOADED",
        safe_capacity=safe_capacity
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session.to_dict()

@router.post("/use-demo")
async def use_demo_video(
    safe_capacity: int = Form(config.DEFAULT_SAFE_CAPACITY),
    db: Session = Depends(get_db)
):
    """Loads or generates the testing demo video for instant verification."""
    demo_path = os.path.join(config.UPLOADS_DIR, "demo_crowd_simulation.mp4")
    
    # If not present, generate it
    if not os.path.exists(demo_path):
        from scripts.generate_test_video import generate_demo_video
        generate_demo_video(demo_path, duration_sec=15)

    session_id = f"SES-{uuid.uuid4().hex[:8].upper()}"
    total_frames, fps, duration = probe_video_metadata(demo_path)

    session = MonitoringSession(
        id=session_id,
        video_name="demo_crowd_simulation.mp4",
        video_path=demo_path,
        duration=duration,
        total_frames=total_frames,
        fps=fps,
        status="UPLOADED",
        safe_capacity=safe_capacity
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return session.to_dict()
