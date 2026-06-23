from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from PIL import Image
import io
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/image-info", tags=["Información de Imagen"])


class ImageInfo(BaseModel):
    filename: str
    format: str
    width: int
    height: int
    mode: str
    size_bytes: int
    size_mb: float
    aspect_ratio: str
    megapixels: float
    recommended_preset: str
    warning: Optional[str] = None


@router.post("/", response_model=ImageInfo, summary="Obtener información de una imagen")
async def get_image_info(file: UploadFile = File(..., description="Imagen a analizar")):
    """
    Analiza una imagen y devuelve información técnica útil antes de vectorizar.
    
    Incluye recomendaciones automáticas basadas en las características de la imagen.
    """
    try:
        # Leer contenido
        content = await file.read()
        size_bytes = len(content)
        size_mb = size_bytes / (1024 * 1024)
        
        # Abrir imagen con PIL
        img = Image.open(io.BytesIO(content))
        width, height = img.size
        mode = img.mode
        format_name = img.format or "Unknown"
        
        # Calcular aspect ratio
        if width > height:
            aspect_ratio = f"{width/height:.2f}:1 (Horizontal)"
        elif height > width:
            aspect_ratio = f"1:{height/width:.2f} (Vertical)"
        else:
            aspect_ratio = "1:1 (Cuadrada)"
        
        # Calcular megapixels
        megapixels = (width * height) / 1_000_000
        
        # Recomendar preset basado en características
        warning = None
        if size_mb > 10:
            warning = "Imagen muy grande (>10MB). Puede tardar en procesarse."
        elif size_mb < 0.1:
            warning = "Imagen muy pequeña. La calidad del vector puede ser limitada."
        
        if megapixels > 5:
            recommended_preset = "ultra_quality"
        elif megapixels > 1:
            recommended_preset = "high_quality"
        elif mode in ["1", "L", "P"]:  # Blanco y negro o escala de grises
            recommended_preset = "black_white"
        else:
            recommended_preset = "color"
        
        # Detectar si es transparente
        if mode in ["RGBA", "LA"] or "transparency" in img.info:
            warning = (warning or "") + " Imagen con transparencia."
        
        return ImageInfo(
            filename=file.filename,
            format=format_name,
            width=width,
            height=height,
            mode=mode,
            size_bytes=size_bytes,
            size_mb=round(size_mb, 2),
            aspect_ratio=aspect_ratio,
            megapixels=round(megapixels, 2),
            recommended_preset=recommended_preset,
            warning=warning
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo analizar la imagen: {str(e)}"
        )