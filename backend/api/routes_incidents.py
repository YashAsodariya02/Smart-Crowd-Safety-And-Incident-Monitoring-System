from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Incident
from services.incident_manager import incident_manager

router = APIRouter(tags=["Incidents"])

@router.get("/api/sessions/{session_id}/incidents")
def get_session_incidents(session_id: str):
    incidents = incident_manager.get_incidents_for_session(session_id)
    return incidents

@router.patch("/api/incidents/{incident_id}/acknowledge")
def acknowledge_incident(incident_id: str):
    res = incident_manager.acknowledge_incident(incident_id)
    if not res:
        raise HTTPException(status_code=404, detail="Incident not found")
    return res

@router.patch("/api/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: str):
    res = incident_manager.resolve_incident(incident_id)
    if not res:
        raise HTTPException(status_code=404, detail="Incident not found")
    return res
