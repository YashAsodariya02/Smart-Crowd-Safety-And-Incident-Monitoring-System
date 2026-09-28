import torch
import psutil
from fastapi import APIRouter
from ai.model_manager import model_manager

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/status")
def get_system_status():
    mem = psutil.virtual_memory()
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"

    models_info = model_manager.get_system_status()

    return {
        "device": device_name,
        "cuda_available": cuda_available,
        "memory_percent": mem.percent,
        "cpu_count": psutil.cpu_count(),
        "models": models_info
    }

@router.post("/download-fire-model")
def download_fire_model():
    success = model_manager.download_verified_fire_smoke_model()
    return {
        "success": success,
        "status": model_manager.fire_smoke_model_status
    }
