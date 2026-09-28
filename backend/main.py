import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import init_db
from ai.model_manager import model_manager
from api import upload_router, sessions_router, incidents_router, system_router, websocket_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Smart Crowd Safety Database...")
    init_db()
    logger.info("Database initialized.")
    logger.info(f"YOLO Person Model: {model_manager.person_model_status}")
    logger.info(f"YOLO Fire/Smoke Model: {model_manager.fire_smoke_model_status}")
    yield
    logger.info("Shutting down Smart Crowd Safety backend...")

app = FastAPI(
    title="Smart Crowd Safety & Incident Monitoring System",
    description="Full-stack AI-powered video monitoring platform with multi-model YOLO detection, temporal stabilization, and real-time telemetry.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload_router)
app.include_router(sessions_router)
app.include_router(incidents_router)
app.include_router(system_router)
app.include_router(websocket_router)

# Mount frontend production build if available
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIST / "index.html")
else:
    @app.get("/")
    def root():
        return {
            "system": "SMART CROWD SAFETY & INCIDENT MONITORING SYSTEM",
            "status": "ONLINE",
            "version": "1.0.0",
            "models": model_manager.get_system_status()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
