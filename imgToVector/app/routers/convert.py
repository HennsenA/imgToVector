import os
import zipfile
import tempfile
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from pathlib import Path

from app.models.schemas import VectorizeParams, Preset, ColorMode, HierarchicalMode, VectorizeMode
from app.services.vectorizer import (
    validate_image_extension,
    generate_unique_filename,
    vectorize_image,
    cleanup_file,
    UPLOADS_DIR,
    OUTPUTS_DIR,
)

router = APIRouter(prefix="/convert", tags=["Conversión"])


@router.post("/", summary="Vectorizar una o más imágenes")
async def convert_images(
    files: List[UploadFile] = File(..., description="Una o más imágenes a vectorizar"),
    preset: Preset = Form(default=Preset.COLOR, description="Preset de vectorización"),
    colormode: ColorMode = Form(default=ColorMode.COLOR),
    hierarchical: HierarchicalMode = Form(default=HierarchicalMode.STACKED),
    mode: VectorizeMode = Form(default=VectorizeMode.SPLINE),
    filter_speckle: int = Form(default=4),
    color_precision: int = Form(default=6),
    layer_difference: int = Form(default=16),
    corner_threshold: int = Form(default=60),
    length_threshold: float = Form(default=4.0),
    max_iterations: int = Form(default=10),
    splice_threshold: int = Form(default=45),
    path_precision: int = Form(default=3),
):
    """
    Sube una o más imágenes y las convierte a SVG.
    
    - Si subes **1 imagen**: devuelve el SVG directamente.
    - Si subes **2 o más imágenes**: devuelve un archivo ZIP con todos los SVGs.
    """
    # Construir parámetros
    params = VectorizeParams(
        preset=preset,
        colormode=colormode,
        hierarchical=hierarchical,
        mode=mode,
        filter_speckle=filter_speckle,
        color_precision=color_precision,
        layer_difference=layer_difference,
        corner_threshold=corner_threshold,
        length_threshold=length_threshold,
        max_iterations=max_iterations,
        splice_threshold=splice_threshold,
        path_precision=path_precision,
    )
    
    # Validar que se recibió al menos un archivo
    if not files or len(files) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes subir al menos una imagen.",
        )
    
    uploaded_paths = []
    svg_paths = []
    
    try:
        # Procesar cada imagen
        for file in files:
            # Validar extensión
            if not validate_image_extension(file.filename):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Formato no soportado: {file.filename}. "
                           f"Formatos permitidos: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP.",
                )
            
            # Guardar imagen temporalmente
            unique_name = generate_unique_filename(file.filename)
            upload_path = UPLOADS_DIR / unique_name
            
            content = await file.read()
            with open(upload_path, "wb") as f:
                f.write(content)
            
            uploaded_paths.append(str(upload_path))
            
            # Vectorizar
            svg_path = vectorize_image(str(upload_path), params)
            svg_paths.append((file.filename, svg_path))
        
        # Decidir qué devolver según la cantidad de imágenes
        if len(svg_paths) == 1:
            # Una sola imagen: devolver el SVG directamente
            original_name, svg_path = svg_paths[0]
            download_name = Path(original_name).stem + ".svg"
            
            return FileResponse(
                path=svg_path,
                media_type="image/svg+xml",
                filename=download_name,
                headers={"X-Original-Name": original_name},
            )
        else:
            # Múltiples imágenes: crear ZIP
            zip_path = OUTPUTS_DIR / f"{Path(files[0].filename).stem}_batch.zip"
            
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for original_name, svg_path in svg_paths:
                    svg_filename = Path(original_name).stem + ".svg"
                    zipf.write(svg_path, arcname=svg_filename)
            
            return FileResponse(
                path=str(zip_path),
                media_type="application/zip",
                filename=zip_path.name,
                headers={"Content-Disposition": f'attachment; filename="{zip_path.name}"'},
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la vectorización: {str(e)}",
        )
    finally:
        # Limpiar imágenes subidas (los SVGs se mantienen para descarga)
        for path in uploaded_paths:
            cleanup_file(path)


@router.get("/presets", summary="Listar presets disponibles")
async def list_presets():
    """Devuelve la lista de presets disponibles con su descripción."""
    return {
        "presets": [
            {
                "id": "color",
                "name": "Color",
                "description": "Vectorización a color con curvas suaves. Ideal para ilustraciones y fotos.",
            },
            {
                "id": "black_white",
                "name": "Blanco y Negro",
                "description": "Vectorización monocromática. Ideal para logos y siluetas.",
            },
            {
                "id": "high_quality",
                "name": "Alta Calidad",
                "description": "Máxima fidelidad. Más lento pero con mejor detalle.",
            },
            {
                "id": "fast",
                "name": "Rápido",
                "description": "Vectorización veloz con menor detalle. Útil para previsualizaciones.",
            },
            {
                "id": "ultra_quality",
                "name": "Ultra Calidad",
                "description": "Máxima precisión posible. Ideal para imágenes complejas con muchos detalles. Archivos grandes.",
            },
        ]
    }