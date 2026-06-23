from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import convert

# Crear la instancia de FastAPI
app = FastAPI(
    title="imgtovector",
    description="API para convertir imágenes rasterizadas a vectores SVG usando vtracer.",
    version="0.2.0",
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(convert.router)


@app.get("/", tags=["Root"])
def root():
    """Mensaje de bienvenida de la API."""
    return {
        "mensaje": "Bienvenido a imgtovector 🎨",
        "documentacion": "/docs",
        "version": "0.2.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de salud de la API."""
    return {
        "status": "ok",
        "service": "imgtovector",
        "version": "0.2.0",
    }