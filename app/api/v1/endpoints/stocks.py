"""
Stock Data Endpoints
Handles stock list and summary data retrieval
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any

from app.models.schemas import AllStocksResponse, StockSummaryResponse
from app.services.stock_service import StockService
from app.core.config import settings

router = APIRouter()
stock_service = StockService()


@router.get("/", response_model=AllStocksResponse, summary="Get all stocks")
async def get_all_stocks() -> AllStocksResponse:
    """
    Retrieve list of all available stock symbols
    
    Returns:
        AllStocksResponse: List of all stock symbols
    """
    try:
        stocks = await stock_service.get_all_stocks()
        return AllStocksResponse(all_stocks=stocks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")


@router.get("/{stock}", response_model=StockSummaryResponse, summary="Get stock summary")
async def get_stock_summary(
    stock: str = Path(..., description="Stock symbol (e.g., RELIANCE, TCS)")
) -> StockSummaryResponse:
    """
    Retrieve historical and live data for a specific stock
    
    Args:
        stock: Stock symbol in uppercase
        
    Returns:
        StockSummaryResponse: Historical and live data for the stock
    """
    try:
        summary = await stock_service.get_stock_summary(stock.upper())
        return summary
    except FileNotFoundError:
        raise HTTPException(
            status_code=404, 
            detail=f"Stock data not found for {stock.upper()}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching stock summary: {str(e)}"
        )


@router.get("/favorites/list", summary="Get favorite stocks")
async def get_favorite_stocks() -> Dict[str, Any]:
    """
    Retrieve list of favorite stocks from favorites.txt
    
    Returns:
        Dict containing list of favorite stock symbols
    """
    try:
        favorites = await stock_service.get_favorites()
        return {"favorites": favorites}
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error fetching favorites: {str(e)}"
        )
