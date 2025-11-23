"""
File Upload Endpoints
Handles Excel file uploads (Historical.xlsx and Live.xlsx)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Dict, Any
import shutil
from pathlib import Path
import os

from app.core.config import settings
from app.core.database_sqlalchemy import db
from app.services.data_processor import DataProcessorService

router = APIRouter()
data_processor = DataProcessorService()


@router.post("/excel-files", summary="Upload Historical and Live Excel files")
async def upload_excel_files(
    background_tasks: BackgroundTasks,
    historical_file: UploadFile = File(..., description="Historical.xlsx file"),
    live_file: UploadFile = File(..., description="Live.xlsx file")
) -> Dict[str, Any]:
    """
    Upload Historical.xlsx and Live.xlsx files.
    This will:
    1. Delete existing Excel files
    2. Save new files
    3. Process data and save to SQLite database
    4. Clear all old data before inserting new data
    
    Returns status and processing information
    """
    # Validate file extensions
    if not historical_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Historical file must be an Excel file (.xlsx or .xls)")
    
    if not live_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Live file must be an Excel file (.xlsx or .xls)")
    
    try:
        live_data_dir = Path(settings.LIVE_DATA_DIR)
        live_data_dir.mkdir(parents=True, exist_ok=True)
        
        hist_path = live_data_dir / "Historical.xlsx"
        live_path = live_data_dir / "Live.xlsx"
        
        # Delete existing files if they exist
        if hist_path.exists():
            os.remove(hist_path)
            print(f"Deleted existing {hist_path}")
        
        if live_path.exists():
            os.remove(live_path)
            print(f"Deleted existing {live_path}")
        
        # Save Historical file
        with hist_path.open("wb") as buffer:
            shutil.copyfileobj(historical_file.file, buffer)
        hist_size = hist_path.stat().st_size
        
        # Save Live file
        with live_path.open("wb") as buffer:
            shutil.copyfileobj(live_file.file, buffer)
        live_size = live_path.stat().st_size
        
        # Log uploads
        db.log_file_upload("Historical", historical_file.filename, hist_size)
        db.log_file_upload("Live", live_file.filename, live_size)
        
        # Process data immediately (not in background)
        print("\n🚀 Starting data processing...")
        result = data_processor.process_all_stocks(clear_existing=True)
        
        return {
            "status": "success",
            "message": "Files uploaded and processed successfully",
            "files_uploaded": {
                "historical": {
                    "filename": historical_file.filename,
                    "size_bytes": hist_size,
                    "saved_as": "Historical.xlsx"
                },
                "live": {
                    "filename": live_file.filename,
                    "size_bytes": live_size,
                    "saved_as": "Live.xlsx"
                }
            },
            "processing_result": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading files: {str(e)}"
        )
    finally:
        historical_file.file.close()
        live_file.file.close()


@router.post("/process", summary="Manually trigger data processing")
async def manual_process() -> Dict[str, Any]:
    """
    Manually trigger processing of existing Excel files
    Useful if you want to reprocess without uploading again
    """
    try:
        result = data_processor.process_all_stocks(clear_existing=True)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing data: {str(e)}"
        )


@router.get("/status", summary="Get processing status")
async def get_processing_status() -> Dict[str, Any]:
    """
    Get information about the last processing run
    """
    last_info = db.get_last_processing_info()
    
    if last_info:
        return {
            "status": "success",
            "last_processing": last_info
        }
    
    return {
        "status": "no_data",
        "message": "No processing has been performed yet"
    }


@router.delete("/data", summary="Clear all stock data")
async def clear_all_data() -> Dict[str, Any]:
    """
    Clear all stock data from database
    (Does not delete Excel files)
    """
    try:
        db.clear_stock_data()
        return {
            "status": "success",
            "message": "All stock data cleared from database"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing data: {str(e)}"
        )
