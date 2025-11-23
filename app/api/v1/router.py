"""
API v1 Router
Aggregates all API endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import stocks, data_processing, upload, background


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(data_processing.router, prefix="/process", tags=["data-processing"])
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(background.router, tags=["background"])
