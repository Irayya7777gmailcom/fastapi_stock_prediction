"""
Background Processor Service
Automatically processes Excel files at regular intervals
"""
import asyncio
from datetime import datetime, time
from typing import Optional

from app.services.data_processor import DataProcessorService
from app.core.config import settings


class BackgroundProcessor:
    """Background task for automatic data processing"""
    
    def __init__(self, process_interval: int = 6):
        """
        Initialize background processor
        
        Args:
            process_interval: Seconds between processing runs (default: 6)
        """
        self.processor = DataProcessorService()
        self.process_interval = process_interval
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
    
    def is_market_hours(self) -> bool:
        """
        Check if current time is within market hours
        
        NSE Trading Hours: 9:15 AM - 3:30 PM IST
        """
        now = datetime.now().time()
        market_open = time(9, 15)   # 9:15 AM
        market_close = time(15, 30)  # 3:30 PM
        
        return market_open <= now <= market_close
    
    async def process_loop(self):
        """
        Main processing loop
        
        - During market hours: Process every 6 seconds
        - Outside market hours: Sleep for 5 minutes
        """
        print("🚀 Background processor started")
        
        while self.is_running:
            try:
                if self.is_market_hours():
                    # Market is open - process frequently
                    print(f"\n[{datetime.now():%H:%M:%S}] 📊 Processing stocks...")
                    
                    start_time = datetime.now()
                    result = self.processor.process_all_stocks(clear_existing=True)
                    elapsed = (datetime.now() - start_time).total_seconds()
                    
                    print(f"   ✅ {result['stocks_processed']}/{result['total_stocks']} stocks updated in {elapsed:.2f}s")
                    
                    # Wait for remaining time to reach process_interval
                    sleep_time = max(1, self.process_interval - elapsed)
                    await asyncio.sleep(sleep_time)
                    
                else:
                    # Market is closed - check less frequently
                    now_str = datetime.now().strftime("%H:%M:%S")
                    print(f"[{now_str}] 🌙 Market closed. Next check in 5 minutes...")
                    await asyncio.sleep(300)  # 5 minutes
                    
            except Exception as e:
                print(f"❌ Background processor error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def start(self):
        """Start the background processor"""
        if self.is_running:
            print("⚠️  Background processor already running")
            return
        
        self.is_running = True
        self.task = asyncio.create_task(self.process_loop())
        print("✅ Background processor task created")
    
    async def stop(self):
        """Stop the background processor"""
        if not self.is_running:
            print("⚠️  Background processor not running")
            return
        
        self.is_running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        print("🛑 Background processor stopped")
    
    def get_status(self) -> dict:
        """Get current processor status"""
        return {
            "is_running": self.is_running,
            "is_market_hours": self.is_market_hours(),
            "process_interval": self.process_interval,
            "last_process_time": self.processor.last_process_time,
            "last_process_count": self.processor.last_process_count
        }


# Global instance
background_processor = BackgroundProcessor(process_interval=6)
