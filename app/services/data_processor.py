"""
Data Processor Service
Handles Excel file processing and SQLite storage
Optimized version without continuous background processing
"""
import os
import pandas as pd
import json
import re
from datetime import datetime
from io import BytesIO
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import settings
from app.core.database_sqlalchemy import db
from app.models.schemas import ProcessStatusResponse
from app.services.excel_utils import ExcelUtils


class DataProcessorService:
    """Service for processing Excel data and saving to SQLite"""
    
    def __init__(self):
        self.live_data_dir = Path(settings.LIVE_DATA_DIR)
        self.hist_file = settings.HIST_FILE
        self.live_file = settings.LIVE_FILE
        self.all_stocks = settings.ALL_STOCKS
        self.utils = ExcelUtils()
        
        # Ensure directories exist
        self.live_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.last_process_time: Optional[datetime] = None
        self.last_process_count: int = 0
    
    def process_all_stocks(self, clear_existing=True):
        """
        Process all stocks and save to SQLite database
        
        Args:
            clear_existing: If True, clears existing data before processing
        """
        print(f"\n[{datetime.now():%H:%M:%S}] Processing {len(self.all_stocks)} stocks...")
        
        live_path = self.live_data_dir / self.live_file
        hist_path = self.live_data_dir / self.hist_file
        
        if not live_path.exists() or not hist_path.exists():
            msg = f"Missing files. Expected: {hist_path} and {live_path}"
            print(f"   {msg}")
            db.log_processing("full_process", 0, "error", msg)
            return {"status": "error", "message": msg}
        
        # Clear existing data if requested
        if clear_existing:
            print("   Clearing existing data...")
            db.clear_stock_data()
        
        success = 0
        errors = []
        
        for stock in self.all_stocks:
            try:
                # Extract data
                hist = self.utils.extract_historical_table(hist_path, stock)
                live = self.utils.extract_live_table(live_path, hist_path, stock)
                
                # Save to database using bulk insert (faster)
                if hist:
                    db.bulk_insert_historical(stock, hist)
                
                if live:
                    db.bulk_insert_live(stock, live)
                
                if hist or live:
                    success += 1
            except Exception as e:
                errors.append(f"{stock}: {str(e)}")
                print(f"   [ERROR] {stock}: {e}")
        
        self.last_process_time = datetime.now()
        self.last_process_count = success
        
        status_msg = f"Processed {success}/{len(self.all_stocks)} stocks successfully"
        if errors:
            status_msg += f". {len(errors)} errors occurred."
        
        print(f"   {status_msg}")
        db.log_processing("full_process", success, "success", status_msg)
        
        return {
            "status": "success",
            "stocks_processed": success,
            "total_stocks": len(self.all_stocks),
            "errors": errors[:10]  # Return first 10 errors
        }
    
    def process_single_stock(self, stock: str):
        """Process a single stock"""
        live_path = self.live_data_dir / self.live_file
        hist_path = self.live_data_dir / self.hist_file
        
        if not live_path.exists() or not hist_path.exists():
            return {"status": "error", "message": "Excel files not found"}
        
        try:
            # Clear existing data for this stock
            db.clear_stock_data(stock)
            
            # Extract and save data
            hist = self.utils.extract_historical_table(hist_path, stock)
            live = self.utils.extract_live_table(live_path, hist_path, stock)
            
            # Use bulk insert for better performance
            if hist:
                db.bulk_insert_historical(stock, hist)
            
            if live:
                db.bulk_insert_live(stock, live)
            
            return {
                "status": "success",
                "stock": stock,
                "historical_rows": len(hist),
                "live_rows": len(live)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_status(self) -> ProcessStatusResponse:
        """Get current processing status"""
        if self.last_process_time:
            return ProcessStatusResponse(
                status="completed",
                message="Last processing completed successfully",
                stocks_processed=self.last_process_count,
                timestamp=self.last_process_time.isoformat()
            )
        return ProcessStatusResponse(
            status="idle",
            message="No processing has been performed yet"
        )
