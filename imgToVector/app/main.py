from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import convert, convert_async, cleanup, image_info

# Crear la instancia de FastAPI
app = FastAPI(
    title="imgtovector",
    description="API para convertir imágenes rasterizadas a vectores SVG usando vtracer.",
    version="0.3.0",
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
app.include_router(convert_async.router)
app.include_router(cleanup.router)
app.include_router(image_info.router)

# Servir archivos estáticos (frontend)
static_path = Path("app/static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/", tags=["Root"])
def root():
    """Redirige al frontend."""
    return FileResponse("app/static/index.html")


@app.get("/health", tags=["Health"])
def health_check():
    """Endpoint de salud de la API."""
    return {
        "status": "ok",
        "service": "imgtovector",
        "version": "0.3.0",
    }