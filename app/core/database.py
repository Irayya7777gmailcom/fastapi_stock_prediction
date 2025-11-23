"""
SQLite Database Connection and Schema
Optimized storage for stock data
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional
from datetime import datetime

from app.core.config import settings


class Database:
    """SQLite database manager"""
    
    def __init__(self):
        self.db_path = Path(settings.BASE_DIR) / "options_data.db"
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for historical data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historical_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock TEXT NOT NULL,
                    category TEXT,
                    strike TEXT,
                    prev_oi TEXT,
                    latest_oi TEXT,
                    call_oi_difference TEXT,
                    put_oi_difference TEXT,
                    ltp TEXT,
                    additional_strike TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for faster stock lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_historical_stock 
                ON historical_data(stock)
            """)
            
            # Table for live data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS live_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock TEXT NOT NULL,
                    section TEXT,
                    label TEXT,
                    prev_oi TEXT,
                    strike TEXT,
                    oi_diff TEXT,
                    is_new_strike TEXT,
                    add_strike TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for faster stock lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_live_stock 
                ON live_data(stock)
            """)
            
            # Table for processing metadata
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processing_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    process_type TEXT NOT NULL,
                    stocks_processed INTEGER,
                    status TEXT,
                    message TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for uploaded files tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_type TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    file_size INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def clear_stock_data(self, stock: Optional[str] = None):
        """Clear stock data (all stocks or specific stock)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if stock:
                cursor.execute("DELETE FROM historical_data WHERE stock = ?", (stock.upper(),))
                cursor.execute("DELETE FROM live_data WHERE stock = ?", (stock.upper(),))
            else:
                cursor.execute("DELETE FROM historical_data")
                cursor.execute("DELETE FROM live_data")
            conn.commit()
    
    def insert_historical_data(self, stock: str, data: dict):
        """Insert historical data for a stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO historical_data 
                (stock, category, strike, prev_oi, latest_oi, call_oi_difference, 
                 put_oi_difference, ltp, additional_strike)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock.upper(),
                data.get("Category", ""),
                data.get("Strike", ""),
                data.get("Prev_OI", ""),
                data.get("Latest_OI", ""),
                data.get("Call_OI_Difference", ""),
                data.get("Put_OI_Difference", ""),
                data.get("LTP", ""),
                data.get("Additional_Strike", "")
            ))
            conn.commit()
    
    def insert_live_data(self, stock: str, data: dict):
        """Insert live data for a stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO live_data 
                (stock, section, label, prev_oi, strike, oi_diff, is_new_strike, add_strike)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                stock.upper(),
                data.get("Section", ""),
                data.get("Label", ""),
                data.get("Prev_OI", ""),
                data.get("Strike", ""),
                data.get("OI_Diff", ""),
                data.get("Is_NewStrike", ""),
                data.get("Add_Strike", "")
            ))
            conn.commit()
    
    def get_historical_data(self, stock: str) -> list:
        """Get historical data for a stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stock, category, strike, prev_oi, latest_oi, 
                       call_oi_difference, put_oi_difference, ltp, additional_strike
                FROM historical_data 
                WHERE stock = ?
                ORDER BY id
            """, (stock.upper(),))
            
            rows = cursor.fetchall()
            return [
                {
                    "Stock": row["stock"],
                    "Category": row["category"],
                    "Strike": row["strike"],
                    "Prev_OI": row["prev_oi"],
                    "Latest_OI": row["latest_oi"],
                    "Call_OI_Difference": row["call_oi_difference"],
                    "Put_OI_Difference": row["put_oi_difference"],
                    "LTP": row["ltp"],
                    "Additional_Strike": row["additional_strike"]
                }
                for row in rows
            ]
    
    def get_live_data(self, stock: str) -> list:
        """Get live data for a stock"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stock, section, label, prev_oi, strike, oi_diff, is_new_strike, add_strike
                FROM live_data 
                WHERE stock = ?
                ORDER BY id
            """, (stock.upper(),))
            
            rows = cursor.fetchall()
            return [
                {
                    "Stock": row["stock"],
                    "Section": row["section"],
                    "Label": row["label"],
                    "Prev_OI": row["prev_oi"],
                    "Strike": row["strike"],
                    "OI_Diff": row["oi_diff"],
                    "Is_NewStrike": row["is_new_strike"],
                    "Add_Strike": row["add_strike"]
                }
                for row in rows
            ]
    
    def get_all_stocks_from_db(self) -> list:
        """Get list of all stocks that have data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT stock FROM (
                    SELECT stock FROM historical_data
                    UNION
                    SELECT stock FROM live_data
                )
                ORDER BY stock
            """)
            return [row["stock"] for row in cursor.fetchall()]
    
    def log_processing(self, process_type: str, stocks_processed: int, status: str, message: str):
        """Log processing metadata"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO processing_metadata 
                (process_type, stocks_processed, status, message)
                VALUES (?, ?, ?, ?)
            """, (process_type, stocks_processed, status, message))
            conn.commit()
    
    def log_file_upload(self, file_type: str, file_name: str, file_size: int):
        """Log file upload"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO uploaded_files 
                (file_type, file_name, file_size)
                VALUES (?, ?, ?)
            """, (file_type, file_name, file_size))
            conn.commit()
    
    def get_last_processing_info(self) -> Optional[dict]:
        """Get last processing information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT process_type, stocks_processed, status, message, processed_at
                FROM processing_metadata
                ORDER BY processed_at DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "process_type": row["process_type"],
                    "stocks_processed": row["stocks_processed"],
                    "status": row["status"],
                    "message": row["message"],
                    "processed_at": row["processed_at"]
                }
            return None


# Global database instance
db = Database()
