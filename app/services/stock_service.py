"""
Stock Service
Business logic for stock data operations
Reads from SQLite database instead of JSON files
"""
import json
import os
from typing import List
from pathlib import Path

from app.models.schemas import StockSummaryResponse, HistoricalDataRow, LiveDataRow
from app.core.config import settings
from app.core.database_sqlalchemy import db


class StockService:
    """Service for handling stock data operations"""
    
    def __init__(self):
        self.base_dir = Path(settings.BASE_DIR)
    
    async def get_all_stocks(self) -> List[str]:
        """
        Get list of all available stocks from database
        
        Returns:
            List of stock symbols
        """
        # Get stocks from database
        stocks_from_db = db.get_all_stocks_from_db()
        
        if stocks_from_db:
            return stocks_from_db
        
        # Fallback to config if database is empty
        return settings.ALL_STOCKS
    
    async def get_stock_summary(self, stock: str) -> StockSummaryResponse:
        """
        Get historical and live data for a specific stock from database
        
        Args:
            stock: Stock symbol in uppercase
            
        Returns:
            StockSummaryResponse with historical and live data
        """
        # Get data from database
        historical_data = db.get_historical_data(stock.upper())
        live_data = db.get_live_data(stock.upper())
        
        # Convert to Pydantic models
        historical = [HistoricalDataRow(**row) for row in historical_data]
        live = [LiveDataRow(**row) for row in live_data]
        
        return StockSummaryResponse(historical=historical, live=live)
    
    async def get_favorites(self) -> List[str]:
        """
        Get list of favorite stocks from favorites.txt
        
        Returns:
            List of favorite stock symbols
        """
        favorites_path = self.base_dir / "favorites.txt"
        
        if not favorites_path.exists():
            return []
        
        with open(favorites_path, "r", encoding="utf-8") as f:
            favorites = [line.strip() for line in f if line.strip()]
        
        return favorites
