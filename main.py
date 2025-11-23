"""
FastAPI Main Application
Options Dashboard - Live OI Tracker
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.data_processor import DataProcessorService
from app.services.background_processor import background_processor


# Configuration: Set to True to enable automatic background processing
ENABLE_BACKGROUND_PROCESSOR = False  # Change to True for production


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"📁 Processed data directory: {settings.PROCESSED_DIR}")
    print(f"📊 Live data directory: {settings.LIVE_DATA_DIR}")
    
    # Ensure directories exist
    os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
    os.makedirs(settings.LIVE_DATA_DIR, exist_ok=True)
    
    # Start background processor if enabled
    if ENABLE_BACKGROUND_PROCESSOR:
        print("🔄 Starting background processor...")
        await background_processor.start()
    else:
        print("ℹ️  Background processor disabled. Use manual refresh or enable in main.py")
    
    yield
    
    # Shutdown
    print("👋 Shutting down application")
    if ENABLE_BACKGROUND_PROCESSOR:
        await background_processor.stop()


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get project directory paths
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    html_path = TEMPLATES_DIR / "index.html"
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Options Dashboard API</h1><p>Visit <a href='/api/docs'>/api/docs</a> for API documentation</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.VERSION
    }


if __name__ == "__main__":
    import uvicorn
    
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
