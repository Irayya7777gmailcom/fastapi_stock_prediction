"""
Data Processing Endpoints
Handles data refresh and processing operations
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime

from app.models.schemas import ProcessStatusResponse
from app.services.data_processor import DataProcessorService

router = APIRouter()
data_processor = DataProcessorService()


@router.post("/refresh", response_model=ProcessStatusResponse, summary="Trigger data refresh")
async def refresh_data(background_tasks: BackgroundTasks) -> ProcessStatusResponse:
    """
    Trigger a manual data refresh/processing
    
    This endpoint will process the Excel files and regenerate JSON data.
    Processing happens in the background.
    
    Returns:
        ProcessStatusResponse: Status of the processing operation
    """
    try:
        # Add processing task to background
        background_tasks.add_task(data_processor.process_all_stocks)
        
        return ProcessStatusResponse(
            status="processing",
            message="Data refresh initiated in background",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initiating data refresh: {str(e)}"
        )


@router.get("/status", response_model=ProcessStatusResponse, summary="Get processing status")
async def get_processing_status() -> ProcessStatusResponse:
    """
    Get current status of data processing
    
    Returns:
        ProcessStatusResponse: Current processing status
    """
    try:
        status = await data_processor.get_status()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching status: {str(e)}"
        )
