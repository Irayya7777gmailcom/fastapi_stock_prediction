"""
Service Layer Tests
"""
import pytest
from pathlib import Path
from app.services.stock_service import StockService
from app.services.excel_utils import ExcelUtils


@pytest.fixture
def stock_service():
    """Fixture for stock service"""
    return StockService()


@pytest.fixture
def excel_utils():
    """Fixture for excel utils"""
    return ExcelUtils()


class TestStockService:
    """Test StockService class"""
    
    @pytest.mark.asyncio
    async def test_get_all_stocks(self, stock_service):
        """Test getting all stocks"""
        stocks = await stock_service.get_all_stocks()
        assert isinstance(stocks, list)
        assert len(stocks) > 0
    
    @pytest.mark.asyncio
    async def test_get_stock_summary(self, stock_service):
        """Test getting stock summary"""
        summary = await stock_service.get_stock_summary("RELIANCE")
        assert hasattr(summary, "historical")
        assert hasattr(summary, "live")
    
    @pytest.mark.asyncio
    async def test_get_favorites(self, stock_service):
        """Test getting favorites"""
        favorites = await stock_service.get_favorites()
        assert isinstance(favorites, list)


class TestExcelUtils:
    """Test ExcelUtils class"""
    
    def test_format_number(self, excel_utils):
        """Test number formatting"""
        assert excel_utils.format_number(1000) == "1,000"
        assert excel_utils.format_number(1000000) == "1,000,000"
        assert excel_utils.format_number("") == ""
        assert excel_utils.format_number(None) == ""
    
    def test_to_number(self, excel_utils):
        """Test string to number conversion"""
        assert excel_utils.to_number("1000") == 1000.0
        assert excel_utils.to_number("1,000") == 1000.0
        assert excel_utils.to_number("(1000)") == -1000.0
        assert excel_utils.to_number("") is None
        assert excel_utils.to_number(None) is None
    
    def test_strike_key(self, excel_utils):
        """Test strike key generation"""
        assert excel_utils.strike_key("3000") == 3000
        assert excel_utils.strike_key("3000.0") == 3000
        assert excel_utils.strike_key("") == ""
