from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Crear la instancia de FastAPI
app = FastAPI(
    title="imgtovector",
    description="API para convertir imágenes rasterizadas a vectores SVG usando vtracer.",
    version="0.1.0",
)

# Configuración CORS (útil cuando conectemos el frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    """Mensaje de bienvenida de la API."""
    return {
        "mensaje": "Bienvenido a imgtovector 🎨",
        "documentacion": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de salud de la API.
    Sirve para verificar que el servicio está activo y operativo.
    """
    return {
        "status": "ok",
        "service": "imgtovector",
        "version": "0.1.0",
    }