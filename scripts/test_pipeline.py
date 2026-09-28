import sys
import os
import time

sys.path.append("backend")
from database.database import init_db, SessionLocal
from database.models import MonitoringSession, Incident, CrowdMetric
from ai.model_manager import model_manager
from ai.video_processor import session_manager

def test_pipeline():
    init_db()
    test_video = "backend/uploads/demo_crowd_simulation.mp4"
    if not os.path.exists(test_video):
        print(f"Error: {test_video} not found")
        return

    session_id = "SES-TEST01"
    db = SessionLocal()
    # Clean up old test data if present
    db.query(MonitoringSession).filter(MonitoringSession.id == session_id).delete()
    db.query(Incident).filter(Incident.session_id == session_id).delete()
    db.query(CrowdMetric).filter(CrowdMetric.session_id == session_id).delete()
    
    session = MonitoringSession(
        id=session_id,
        video_name="demo_crowd_simulation.mp4",
        video_path=os.path.abspath(test_video),
        safe_capacity=30
    )
    db.add(session)
    db.commit()
    db.close()

    print(f"Created session {session_id}, starting processor...")
    processor = session_manager.create_processor(session_id, os.path.abspath(test_video), safe_capacity=30)
    processor.start()

    # Let it run for 4 seconds
    time.sleep(4.0)
    
    processor.stop()
    print("Processor stopped. Checking results...")

    # Check metrics in DB
    db = SessionLocal()
    metrics = db.query(CrowdMetric).filter(CrowdMetric.session_id == session_id).all()
    incidents = db.query(Incident).filter(Incident.session_id == session_id).all()
    print(f"Persisted {len(metrics)} crowd metrics to database.")
    for m in metrics[:3]:
        print(f"  Metric: Time {m.video_timestamp} | Persons: {m.person_count} | Occupancy: {m.occupancy}% | Level: {m.crowd_level}")
    
    print(f"Recorded {len(incidents)} incidents.")
    for inc in incidents:
        print(f"  Incident: {inc.id} | {inc.type} [{inc.severity}] | Status: {inc.status} | Time: {inc.timestamp}")

    db.close()
    print("Pipeline test completed successfully!")

if __name__ == "__main__":
    test_pipeline()
