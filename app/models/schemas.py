"""
Pydantic Schemas for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class HistoricalDataRow(BaseModel):
    """Historical data row schema"""
    Stock: str = Field(..., description="Stock symbol")
    Category: str = Field(..., description="Category (Call Resistance/Put Support)")
    Strike: str = Field(..., description="Strike price")
    Prev_OI: str = Field(..., description="Previous Open Interest")
    Latest_OI: str = Field(..., description="Latest Open Interest")
    Call_OI_Difference: str = Field(..., description="Call OI Difference")
    Put_OI_Difference: str = Field(..., description="Put OI Difference")
    LTP: str = Field(..., description="Last Traded Price")
    Additional_Strike: str = Field(default="", description="Additional strike marker")


class LiveDataRow(BaseModel):
    """Live data row schema"""
    Section: str = Field(..., description="Section name (Call Support/Resistance, Put Support/Resistance)")
    Label: str = Field(..., description="Label/identifier")
    Prev_OI: str = Field(..., description="Previous Open Interest")
    Strike: str = Field(..., description="Strike price")
    Stock: str = Field(..., description="Stock symbol")
    OI_Diff: str = Field(..., description="OI Difference")
    Is_NewStrike: str = Field(default="", description="Whether this is a new strike")
    Add_Strike: str = Field(default="", description="Additional strike marker")


class StockSummaryResponse(BaseModel):
    """Stock summary response schema"""
    historical: List[HistoricalDataRow] = Field(default_factory=list, description="Historical data")
    live: List[LiveDataRow] = Field(default_factory=list, description="Live data")


class AllStocksResponse(BaseModel):
    """All stocks list response"""
    all_stocks: List[str] = Field(..., description="List of all stock symbols")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Health status")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")


class ProcessStatusResponse(BaseModel):
    """Data processing status response"""
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    stocks_processed: Optional[int] = Field(None, description="Number of stocks processed")
    timestamp: Optional[str] = Field(None, description="Processing timestamp")
