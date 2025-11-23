"""
SQLAlchemy Models for Stock Data
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class HistoricalData(BaseModel):
    """Historical stock data model"""
    
    __tablename__ = "historical_data"
    
    stock = Column(String(50), nullable=False, index=True)
    category = Column(String(100))
    strike = Column(String(50))
    prev_oi = Column(String(50))
    latest_oi = Column(String(50))
    call_oi_difference = Column(String(50))
    put_oi_difference = Column(String(50))
    ltp = Column(String(50))
    additional_strike = Column(String(50))
    
    __table_args__ = (
        Index('idx_historical_stock', 'stock'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "Stock": self.stock,
            "Category": self.category or "",
            "Strike": self.strike or "",
            "Prev_OI": self.prev_oi or "",
            "Latest_OI": self.latest_oi or "",
            "Call_OI_Difference": self.call_oi_difference or "",
            "Put_OI_Difference": self.put_oi_difference or "",
            "LTP": self.ltp or "",
            "Additional_Strike": self.additional_strike or ""
        }


class LiveData(BaseModel):
    """Live stock data model"""
    
    __tablename__ = "live_data"
    
    stock = Column(String(50), nullable=False, index=True)
    section = Column(String(100))
    label = Column(String(100))
    prev_oi = Column(String(50))
    strike = Column(String(50))
    oi_diff = Column(String(50))
    is_new_strike = Column(String(10))
    add_strike = Column(String(50))
    
    __table_args__ = (
        Index('idx_live_stock', 'stock'),
    )
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "Stock": self.stock,
            "Section": self.section or "",
            "Label": self.label or "",
            "Prev_OI": self.prev_oi or "",
            "Strike": self.strike or "",
            "OI_Diff": self.oi_diff or "",
            "Is_NewStrike": self.is_new_strike or "",
            "Add_Strike": self.add_strike or ""
        }


class ProcessingMetadata(BaseModel):
    """Processing metadata and logs"""
    
    __tablename__ = "processing_metadata"
    
    process_type = Column(String(50), nullable=False)
    stocks_processed = Column(Integer)
    status = Column(String(50))
    message = Column(Text)
    processed_at = Column(DateTime, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "process_type": self.process_type,
            "stocks_processed": self.stocks_processed,
            "status": self.status,
            "message": self.message,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }


class UploadedFile(BaseModel):
    """Uploaded files tracking"""
    
    __tablename__ = "uploaded_files"
    
    file_type = Column(String(50), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            "file_type": self.file_type,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None
        }
