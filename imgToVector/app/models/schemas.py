from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ColorMode(str, Enum):
    """Modo de color para la vectorización."""
    COLOR = "color"
    BINARY = "binary"  # Blanco y negro


class HierarchicalMode(str, Enum):
    """Modo jerárquico de las capas."""
    STACKED = "stacked"  # Capas apiladas (recomendado para color)
    CUTOUT = "cutout"    # Recortado (recomendado para B/N)


class VectorizeMode(str, Enum):
    """Tipo de trazado de las curvas."""
    SPLINE = "spline"    # Curvas suaves (recomendado)
    POLYGON = "polygon"  # Polígonos rectos
    NONE = "none"        # Sin suavizado


class Preset(str, Enum):
    """Presets predefinidos para facilitar la vectorización."""
    COLOR = "color"
    BLACK_WHITE = "black_white"
    HIGH_QUALITY = "high_quality"
    FAST = "fast"
    ULTRA_QUALITY = "ultra_quality"  # ← NUEVO


class VectorizeParams(BaseModel):
    """
    Parámetros para la vectorización con vtracer.
    Todos tienen valores por defecto razonables.
    """
    preset: Optional[Preset] = Field(
        default=Preset.COLOR,
        description="Preset predefinido. Si se usa, sobrescribe los otros parámetros."
    )
    colormode: ColorMode = Field(
        default=ColorMode.COLOR,
        description="Modo de color: 'color' o 'binary' (blanco y negro)."
    )
    hierarchical: HierarchicalMode = Field(
        default=HierarchicalMode.STACKED,
        description="Modo jerárquico: 'stacked' o 'cutout'."
    )
    mode: VectorizeMode = Field(
        default=VectorizeMode.SPLINE,
        description="Tipo de trazado: 'spline', 'polygon' o 'none'."
    )
    filter_speckle: int = Field(
        default=4, ge=0, le=32,
        description="Descarta áreas menores a este tamaño (en px²)."
    )
    color_precision: int = Field(
        default=6, ge=1, le=8,
        description="Precisión del color (mayor = más colores, más lento)."
    )
    layer_difference: int = Field(
        default=16, ge=0, le=128,
        description="Diferencia mínima entre capas adyacentes."
    )
    corner_threshold: int = Field(
        default=60, ge=0, le=180,
        description="Umbral para detectar esquinas (en grados)."
    )
    length_threshold: float = Field(
        default=4.0, ge=0.0,
        description="Longitud mínima de segmento para subdividir."
    )
    max_iterations: int = Field(
        default=10, ge=0, le=20,
        description="Máximo de iteraciones para ajustar curvas."
    )
    splice_threshold: int = Field(
        default=45, ge=0, le=180,
        description="Umbral de empalme de curvas (en grados)."
    )
    path_precision: int = Field(
        default=3, ge=1, le=8,
        description="Decimales en las coordenadas del SVG."
    )


# Presets predefinidos con parámetros optimizados
PRESETS_CONFIG = {
    Preset.COLOR: {
        "colormode": ColorMode.COLOR,
        "hierarchical": HierarchicalMode.STACKED,
        "mode": VectorizeMode.SPLINE,
        "filter_speckle": 4,
        "color_precision": 6,
        "layer_difference": 16,
        "corner_threshold": 60,
        "max_iterations": 10,
        "path_precision": 3,
    },
    Preset.BLACK_WHITE: {
        "colormode": ColorMode.BINARY,
        "hierarchical": HierarchicalMode.CUTOUT,
        "mode": VectorizeMode.SPLINE,
        "filter_speckle": 4,
        "color_precision": 6,
        "layer_difference": 16,
        "corner_threshold": 60,
        "max_iterations": 10,
        "path_precision": 3,
    },
    Preset.HIGH_QUALITY: {
        "colormode": ColorMode.COLOR,
        "hierarchical": HierarchicalMode.STACKED,
        "mode": VectorizeMode.SPLINE,
        "filter_speckle": 2,
        "color_precision": 7,
        "layer_difference": 8,
        "corner_threshold": 80,
        "max_iterations": 15,
        "path_precision": 5,
    },
    Preset.FAST: {
        "colormode": ColorMode.COLOR,
        "hierarchical": HierarchicalMode.STACKED,
        "mode": VectorizeMode.POLYGON,
        "filter_speckle": 8,
        "color_precision": 4,
        "layer_difference": 32,
        "corner_threshold": 45,
        "max_iterations": 5,
        "path_precision": 2,
    },
    # ← AGREGA ESTE NUEVO PRESET
    Preset.ULTRA_QUALITY: {
        "colormode": ColorMode.COLOR,
        "hierarchical": HierarchicalMode.STACKED,
        "mode": VectorizeMode.SPLINE,
        "filter_speckle": 0,      # ← Sin filtrar (máximo detalle)
        "color_precision": 8,     # ← Máxima precisión de color
        "layer_difference": 4,    # ← Detecta diferencias mínimas de color
        "corner_threshold": 100,  # ← Mejor detección de esquinas
        "max_iterations": 20,     # ← Máximas iteraciones para suavizar
        "path_precision": 6,      # ← Buena precisión de coordenadas
    },
}