from api.routes_upload import router as upload_router
from api.routes_sessions import router as sessions_router
from api.routes_incidents import router as incidents_router
from api.routes_system import router as system_router
from api.websocket_endpoint import router as websocket_router

__all__ = ["upload_router", "sessions_router", "incidents_router", "system_router", "websocket_router"]
