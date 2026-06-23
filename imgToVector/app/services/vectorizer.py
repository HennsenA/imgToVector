import os
import uuid
import vtracer
from pathlib import Path
from app.models.schemas import VectorizeParams, PRESETS_CONFIG

# Directorios base
UPLOADS_DIR = Path("uploads")
OUTPUTS_DIR = Path("outputs")

# Asegurar que los directorios existen
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Extensiones soportadas
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif", ".webp"}


def generate_unique_filename(original_filename: str) -> str:
    """Genera un nombre único para evitar colisiones."""
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:10]
    return f"{unique_id}{ext}"


def validate_image_extension(filename: str) -> bool:
    """Valida que la extensión de la imagen sea soportada."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def apply_preset(params: VectorizeParams) -> dict:
    """Aplica el preset seleccionado y devuelve los parámetros finales."""
    config = PRESETS_CONFIG[params.preset].copy()
    return config


def vectorize_image(input_path: str, params: VectorizeParams) -> str:
    """
    Convierte una imagen a SVG usando vtracer.
    
    Args:
        input_path: Ruta absoluta de la imagen de entrada.
        params: Parámetros de vectorización.
    
    Returns:
        Ruta absoluta del archivo SVG generado.
    """
    # Aplicar preset
    config = apply_preset(params)
    
    # Generar nombre único para el SVG
    svg_filename = f"{uuid.uuid4().hex[:10]}.svg"
    output_path = OUTPUTS_DIR / svg_filename
    
    # Ejecutar vtracer - LOS DOS PRIMEROS PARÁMETROS SON POSICIONALES
    vtracer.convert_image_to_svg_py(
        input_path,           # ← Primer parámetro posicional (input)
        str(output_path),     # ← Segundo parámetro posicional (output)
        colormode=config["colormode"].value,
        hierarchical=config["hierarchical"].value,
        mode=config["mode"].value,
        filter_speckle=config.get("filter_speckle", 4),
        color_precision=config.get("color_precision", 6),
        layer_difference=config.get("layer_difference", 16),
        corner_threshold=config.get("corner_threshold", 60),
        length_threshold=config.get("length_threshold", 4.0),
        max_iterations=config.get("max_iterations", 10),
        splice_threshold=config.get("splice_threshold", 45),
        path_precision=config.get("path_precision", 3),
    )
    
    return str(output_path)


def cleanup_file(file_path: str) -> None:
    """Elimina un archivo si existe."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error al limpiar archivo {file_path}: {e}")