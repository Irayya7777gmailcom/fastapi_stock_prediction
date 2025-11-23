"""
Background Processor Control Endpoints
"""
from fastapi import APIRouter, HTTPException
from app.services.background_processor import background_processor

router = APIRouter(prefix="/background", tags=["background"])


@router.get("/status")
async def get_background_status():
    """
    Get background processor status
    
    Returns:
        - is_running: Whether processor is running
        - is_market_hours: Whether current time is within market hours
        - process_interval: Seconds between processing runs
        - last_process_time: Last processing timestamp
        - last_process_count: Number of stocks processed last time
    """
    status = background_processor.get_status()
    return {
        "status": "success",
        "data": status
    }


@router.post("/start")
async def start_background_processor():
    """
    Start the background processor
    
    Note: Usually starts automatically on server startup.
    This endpoint is for manual control if needed.
    """
    try:
        await background_processor.start()
        return {
            "status": "success",
            "message": "Background processor started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
async def stop_background_processor():
    """
    Stop the background processor
    
    Use this to pause automatic processing.
    You can restart it with /start endpoint.
    """
    try:
        await background_processor.stop()
        return {
            "status": "success",
            "message": "Background processor stopped"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/interval/{seconds}")
async def update_process_interval(seconds: int):
    """
    Update the processing interval
    
    Args:
        seconds: New interval in seconds (minimum: 1, recommended: 6)
    """
    if seconds < 1:
        raise HTTPException(status_code=400, detail="Interval must be at least 1 second")
    
    background_processor.process_interval = seconds
    
    return {
        "status": "success",
        "message": f"Process interval updated to {seconds} seconds"
    }
