import os
import zipfile
import asyncio
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse
from pathlib import Path
import uuid

from app.models.schemas import VectorizeParams, Preset
from app.services.vectorizer import (
    validate_image_extension,
    generate_unique_filename,
    vectorize_image,
    cleanup_file,
    UPLOADS_DIR,
    OUTPUTS_DIR,
)

router = APIRouter(prefix="/convert-async", tags=["Conversión Asíncrona"])

# Almacenamiento temporal de tareas (en producción usar Redis o BD)
tasks = {}


async def process_image_task(task_id: str, files: List[UploadFile], params: VectorizeParams):
    """Tarea en segundo plano para procesar imágenes grandes."""
    try:
        tasks[task_id]["status"] = "processing"
        tasks[task_id]["progress"] = 0
        
        uploaded_paths = []
        svg_paths = []
        total_files = len(files)
        
        for idx, file in enumerate(files):
            # Validar extensión
            if not validate_image_extension(file.filename):
                tasks[task_id]["status"] = "failed"
                tasks[task_id]["error"] = f"Formato no soportado: {file.filename}"
                return
            
            # Guardar imagen
            unique_name = generate_unique_filename(file.filename)
            upload_path = UPLOADS_DIR / unique_name
            
            content = await file.read()
            with open(upload_path, "wb") as f:
                f.write(content)
            
            uploaded_paths.append(str(upload_path))
            
            # Vectorizar
            svg_path = vectorize_image(str(upload_path), params)
            svg_paths.append((file.filename, svg_path))
            
            # Actualizar progreso
            tasks[task_id]["progress"] = int(((idx + 1) / total_files) * 100)
        
        # Generar resultado
        if len(svg_paths) == 1:
            original_name, svg_path = svg_paths[0]
            download_name = Path(original_name).stem + ".svg"
            tasks[task_id]["result"] = {
                "type": "single",
                "svg_path": svg_path,
                "download_name": download_name,
                "original_name": original_name,
            }
        else:
            zip_path = OUTPUTS_DIR / f"{Path(files[0].filename).stem}_batch.zip"
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for original_name, svg_path in svg_paths:
                    svg_filename = Path(original_name).stem + ".svg"
                    zipf.write(svg_path, arcname=svg_filename)
            
            tasks[task_id]["result"] = {
                "type": "zip",
                "zip_path": str(zip_path),
                "download_name": zip_path.name,
            }
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        
        # Limpiar uploads
        for path in uploaded_paths:
            cleanup_file(path)
    
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)


@router.post("/", summary="Vectorización asíncrona para imágenes grandes")
async def convert_images_async(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="Una o más imágenes a vectorizar"),
    preset: Preset = Form(default=Preset.COLOR),
):
    """
    Inicia una vectorización asíncrona. Ideal para imágenes grandes o múltiples.
    
    Devuelve un task_id para consultar el progreso.
    """
    task_id = str(uuid.uuid4())
    
    # Crear tarea
    params = VectorizeParams(preset=preset)
    tasks[task_id] = {
        "status": "queued",
        "progress": 0,
        "created_at": str(pd.Timestamp.now()),
        "result": None,
        "error": None,
    }
    
    # Iniciar tarea en background
    background_tasks.add_task(process_image_task, task_id, files, params)
    
    return {
        "task_id": task_id,
        "status": "queued",
        "message": "Procesamiento iniciado. Usa el task_id para consultar el progreso."
    }


@router.get("/{task_id}", summary="Consultar progreso de vectorización")
async def get_task_status(task_id: str):
    """Consulta el estado de una tarea de vectorización."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task = tasks[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "result": task["result"],
        "error": task["error"],
    }


@router.delete("/{task_id}", summary="Eliminar tarea completada")
async def delete_task(task_id: str):
    """Elimina una tarea completada o fallida del almacenamiento temporal."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    task = tasks[task_id]
    
    # Limpiar archivos de resultado
    if task["result"]:
        if task["result"]["type"] == "single":
            cleanup_file(task["result"]["svg_path"])
        elif task["result"]["type"] == "zip":
            cleanup_file(task["result"]["zip_path"])
    
    del tasks[task_id]
    
    return {"message": f"Tarea {task_id} eliminada"}