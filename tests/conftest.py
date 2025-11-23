"""
Pytest Configuration
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture for test data directory"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def sample_stock_data():
    """Fixture for sample stock data"""
    return {
        "historical": [
            {
                "Stock": "RELIANCE",
                "Category": "Call Resistance",
                "Strike": "3000",
                "Prev_OI": "10,000",
                "Latest_OI": "12,000",
                "Call_OI_Difference": "2,000",
                "Put_OI_Difference": "",
                "LTP": "2950",
                "Additional_Strike": ""
            }
        ],
        "live": [
            {
                "Section": "Call Resistance",
                "Label": "R1",
                "Prev_OI": "12,000",
                "Strike": "3000",
                "Stock": "RELIANCE",
                "OI_Diff": "2,000",
                "Is_NewStrike": "",
                "Add_Strike": ""
            }
        ]
    }
