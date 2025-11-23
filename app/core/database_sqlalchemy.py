"""
SQLAlchemy Database Connection and Session Management
"""
from sqlalchemy import create_engine, distinct
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from app.core.config import settings
from app.models.base import Base
from app.models.stock_models import HistoricalData, LiveData, ProcessingMetadata, UploadedFile


class Database:
    """SQLAlchemy database manager"""
    
    def __init__(self):
        self.db_path = Path(settings.BASE_DIR) / "options_data.db"
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False},  # Needed for SQLite
            echo=False  # Set to True for SQL query logging
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.init_database()
    
    def init_database(self):
        """Initialize database schema"""
        Base.metadata.create_all(bind=self.engine)
        print(f"✅ Database initialized: {self.db_path}")
    
    @contextmanager
    def get_session(self):
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_db(self):
        """Dependency for FastAPI endpoints"""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # ==================== Historical Data ====================
    
    def insert_historical_data(self, stock: str, data: dict):
        """Insert historical data for a stock"""
        with self.get_session() as session:
            historical = HistoricalData(
                stock=stock.upper(),
                category=data.get("Category", ""),
                strike=data.get("Strike", ""),
                prev_oi=data.get("Prev_OI", ""),
                latest_oi=data.get("Latest_OI", ""),
                call_oi_difference=data.get("Call_OI_Difference", ""),
                put_oi_difference=data.get("Put_OI_Difference", ""),
                ltp=data.get("LTP", ""),
                additional_strike=data.get("Additional_Strike", "")
            )
            session.add(historical)
    
    def get_historical_data(self, stock: str) -> List[Dict]:
        """Get historical data for a stock"""
        with self.get_session() as session:
            results = session.query(HistoricalData).filter(
                HistoricalData.stock == stock.upper()
            ).order_by(HistoricalData.id).all()
            
            return [result.to_dict() for result in results]
    
    def bulk_insert_historical(self, stock: str, data_list: List[dict]):
        """Bulk insert historical data"""
        with self.get_session() as session:
            objects = [
                HistoricalData(
                    stock=stock.upper(),
                    category=data.get("Category", ""),
                    strike=data.get("Strike", ""),
                    prev_oi=data.get("Prev_OI", ""),
                    latest_oi=data.get("Latest_OI", ""),
                    call_oi_difference=data.get("Call_OI_Difference", ""),
                    put_oi_difference=data.get("Put_OI_Difference", ""),
                    ltp=data.get("LTP", ""),
                    additional_strike=data.get("Additional_Strike", "")
                )
                for data in data_list
            ]
            session.bulk_save_objects(objects)
    
    # ==================== Live Data ====================
    
    def insert_live_data(self, stock: str, data: dict):
        """Insert live data for a stock"""
        with self.get_session() as session:
            live = LiveData(
                stock=stock.upper(),
                section=data.get("Section", ""),
                label=data.get("Label", ""),
                prev_oi=data.get("Prev_OI", ""),
                strike=data.get("Strike", ""),
                oi_diff=data.get("OI_Diff", ""),
                is_new_strike=data.get("Is_NewStrike", ""),
                add_strike=data.get("Add_Strike", "")
            )
            session.add(live)
    
    def get_live_data(self, stock: str) -> List[Dict]:
        """Get live data for a stock"""
        with self.get_session() as session:
            results = session.query(LiveData).filter(
                LiveData.stock == stock.upper()
            ).order_by(LiveData.id).all()
            
            return [result.to_dict() for result in results]
    
    def bulk_insert_live(self, stock: str, data_list: List[dict]):
        """Bulk insert live data"""
        with self.get_session() as session:
            objects = [
                LiveData(
                    stock=stock.upper(),
                    section=data.get("Section", ""),
                    label=data.get("Label", ""),
                    prev_oi=data.get("Prev_OI", ""),
                    strike=data.get("Strike", ""),
                    oi_diff=data.get("OI_Diff", ""),
                    is_new_strike=data.get("Is_NewStrike", ""),
                    add_strike=data.get("Add_Strike", "")
                )
                for data in data_list
            ]
            session.bulk_save_objects(objects)
    
    # ==================== Stock Operations ====================
    
    def get_all_stocks_from_db(self) -> List[str]:
        """Get list of all stocks that have data"""
        with self.get_session() as session:
            # Get distinct stocks from both tables
            hist_stocks = session.query(distinct(HistoricalData.stock)).all()
            live_stocks = session.query(distinct(LiveData.stock)).all()
            
            # Combine and deduplicate
            all_stocks = set([s[0] for s in hist_stocks] + [s[0] for s in live_stocks])
            return sorted(list(all_stocks))
    
    def clear_stock_data(self, stock: Optional[str] = None):
        """Clear stock data (all stocks or specific stock)"""
        with self.get_session() as session:
            if stock:
                session.query(HistoricalData).filter(
                    HistoricalData.stock == stock.upper()
                ).delete()
                session.query(LiveData).filter(
                    LiveData.stock == stock.upper()
                ).delete()
            else:
                session.query(HistoricalData).delete()
                session.query(LiveData).delete()
    
    # ==================== Processing Metadata ====================
    
    def log_processing(self, process_type: str, stocks_processed: int, status: str, message: str):
        """Log processing metadata"""
        with self.get_session() as session:
            metadata = ProcessingMetadata(
                process_type=process_type,
                stocks_processed=stocks_processed,
                status=status,
                message=message,
                processed_at=datetime.utcnow()
            )
            session.add(metadata)
    
    def get_last_processing_info(self) -> Optional[Dict]:
        """Get last processing information"""
        with self.get_session() as session:
            result = session.query(ProcessingMetadata).order_by(
                ProcessingMetadata.processed_at.desc()
            ).first()
            
            return result.to_dict() if result else None
    
    # ==================== File Upload Tracking ====================
    
    def log_file_upload(self, file_type: str, file_name: str, file_size: int):
        """Log file upload"""
        with self.get_session() as session:
            upload = UploadedFile(
                file_type=file_type,
                file_name=file_name,
                file_size=file_size,
                uploaded_at=datetime.utcnow()
            )
            session.add(upload)
    
    def get_recent_uploads(self, limit: int = 10) -> List[Dict]:
        """Get recent file uploads"""
        with self.get_session() as session:
            results = session.query(UploadedFile).order_by(
                UploadedFile.uploaded_at.desc()
            ).limit(limit).all()
            
            return [result.to_dict() for result in results]


# Global database instance
db = Database()
