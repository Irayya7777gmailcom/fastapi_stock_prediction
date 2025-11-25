"""
Application Configuration
Centralized settings management using Pydantic
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application Info
    APP_NAME: str = "Options Dashboard API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Live OI Tracker for Stock Options"
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Directories
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    LIVE_DATA_DIR: str = os.getenv("LIVE_DATA_DIR", str(BASE_DIR / "live_data")).replace("/app", str(BASE_DIR))
    # PROCESSED_DIR: Deprecated - Using SQLite database instead of JSON files
    PROCESSED_DIR: str = os.getenv("PROCESSED_DIR", str(BASE_DIR / "processed")).replace("/app", str(BASE_DIR))
    
    # Data Files
    HIST_FILE: str = "Historical.xlsx"
    LIVE_FILE: str = "Live.xlsx"
    
    # Processing Configuration (DEPRECATED - using on-demand upload API instead)
    REFRESH_INTERVAL: int = 6  # Obsolete - no background processing
    AUTO_PROCESS: bool = False  # Obsolete - upload API triggers processing
    
    # Stock List
    ALL_STOCKS: List[str] = [
        "ABB","ABCAPITAL","ADANIENSOL","ADANIENT","ADANIGREEN","ADANIPORTS","ALKEM","AMBER","AMBUJACEM","ANGELONE",
        "APLAPOLLO","APOLLOHOSP","ASHOKLEY","ASIANPAINT","AINT","ASTRAL","AUBANK","AUROPHARMA","AXISBANK","BAJAJFINSV","BAJFINANCE",
        "BANDHANBNK","BANKBARODA","BANKINDIA","BDL","BEL","BHARATFORG","BHARTIARTL","BHEL","BIOCON","BLUESTARCO",
        "BOSCHLTD","BPCL","BRITANNIA","BSE","CAMS","CANBK","CDSL","CGPOWER","CIPLA","COALINDIA",
        "COFORGE","COLPAL","CONCOR","CROMPTON","CUMMINSIND","CYIENT","DABUR","DALBHARAT","DELHIVERY","DIVISLAB",
        "DIXON","DLF","DMART","DRREDDY","EICHERMOT","ETERNAL","EXIDEIND","FEDERALBNK","FORTIS","GAIL",
        "GLENMARK","GMRAIRPORT","GODREJCP","GODREJPROP","GRASIM","HAL","HAVELLS","HCLTECH","HDFCAMC","HDFCBANK",
        "HDFCLIFE","HEROMOTOCO","HFCL","HINDALCO","HINDPETRO","HINDUNILVR","HINDZINC","HUDCO","ICICIBANK","ICICIGI",
        "IDEA","IDFCFIRSTB","IEX","IGL","IIFL","INDHOTEL","INDIANB","INDIGO","INDUSINDBK","INDUSTOWER",
        "INFY","INOXWIND","IOC","IRCTC","IREDA","IRFC","ITC","JINDALSTEL","JIOFIN","JSWENERGY",
        "JSWSTEEL","JUBLFOOD","KALYANKJIL","KAYNES","KEI","KFINTECH","KOTAKBANK","KPITTECH","LAURUSLABS","LICHSGFIN",
        "LICI","LODHA","LT","LTF","LTIM","LUPIN","MANAPPURAM","MANKIND","MARICO","MARUTI",
        "MAXHEALTH","MAZDOCK","MCX","MFSL","MM","MPHASIS","MUTHOOTFIN","NAUKRI","NATIONALUM","NBCC",
        "NCC","NESTLEIND","NHPC","NMDC","NTPC","NUVAMA","NYKAA","OBEROIRLTY","OFSS","OIL",
        "ONGC","ONE","PAGEIND","PATANJALI","PAYTM","PETRONET","PFC","PGEL","PHOENIXLTD","PIDILITIND",
        "PIIND","PNB","PNBHOUSING","POLICYBZR","POLYCAB","POWERGRID","PPLPHARMA","PRESTIGE","RBLBANK","RECLTD",
        "RELIANCE","RVNL","SAIL","SBICARD","SBILIFE","SBIN","SHREECEM","SHRIRAMFIN","SIEMENS","SOLARINDS",
        "SONACOMS","SRF","SUZLON","SUNPHARMA","SUPREMEIND","SYNGENE","TATACHEM","TATACONSUM","TATAELXSI","TATAMOTORS",
        "TATAPOWER","TATASTEEL","TATATECH","TCS","TECHM","TIINDIA","TITAGARH","TITAN","TORNTPHARM","TORNTPOWER",
        "TRENT","TVSMOTOR","ULTRACEMCO","UNIONBANK","UNITDSPR","UNOMINDA","UPL","VBL","VEDL","VOLTAS",
        "WIPRO","YESBANK","ZYDUSLIFE"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
