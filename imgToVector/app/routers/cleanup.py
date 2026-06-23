import os
import time
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/cleanup", tags=["Limpieza"])

UPLOADS_DIR = Path("uploads")
OUTPUTS_DIR = Path("outputs")


class CleanupResponse(BaseModel):
    files_deleted: int
    space_freed_bytes: int
    space_freed_mb: float
    message: str


@router.delete("/old", response_model=CleanupResponse, summary="Limpiar archivos antiguos")
async def cleanup_old_files(max_age_hours: int = 24):
    """
    Elimina archivos antiguos de las carpetas uploads/ y outputs/.
    
    - **max_age_hours**: Edad máxima de los archivos en horas (default: 24)
    """
    current_time = time.time()
    files_deleted = 0
    space_freed = 0
    max_age_seconds = max_age_hours * 3600
    
    # Limpiar uploads
    if UPLOADS_DIR.exists():
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        space_freed += file_size
                    except Exception as e:
                        print(f"Error al eliminar {file_path}: {e}")
    
    # Limpiar outputs
    if OUTPUTS_DIR.exists():
        for file_path in OUTPUTS_DIR.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        space_freed += file_size
                    except Exception as e:
                        print(f"Error al eliminar {file_path}: {e}")
    
    space_freed_mb = space_freed / (1024 * 1024)
    
    return CleanupResponse(
        files_deleted=files_deleted,
        space_freed_bytes=space_freed,
        space_freed_mb=round(space_freed_mb, 2),
        message=f"Se eliminaron {files_deleted} archivos antiguos (mayores a {max_age_hours}h)"
    )


@router.get("/stats", summary="Estadísticas de almacenamiento")
async def get_storage_stats():
    """Devuelve estadísticas sobre el uso de almacenamiento."""
    def get_dir_stats(directory: Path) -> dict:
        if not directory.exists():
            return {"files": 0, "size_bytes": 0, "size_mb": 0}
        
        files = list(directory.iterdir())
        total_size = sum(f.stat().st_size for f in files if f.is_file())
        
        return {
            "files": len([f for f in files if f.is_file()]),
            "size_bytes": total_size,
            "size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    uploads_stats = get_dir_stats(UPLOADS_DIR)
    outputs_stats = get_dir_stats(OUTPUTS_DIR)
    
    return {
        "uploads": uploads_stats,
        "outputs": outputs_stats,
        "total": {
            "files": uploads_stats["files"] + outputs_stats["files"],
            "size_bytes": uploads_stats["size_bytes"] + outputs_stats["size_bytes"],
            "size_mb": round((uploads_stats["size_bytes"] + outputs_stats["size_bytes"]) / (1024 * 1024), 2)
        }
    }