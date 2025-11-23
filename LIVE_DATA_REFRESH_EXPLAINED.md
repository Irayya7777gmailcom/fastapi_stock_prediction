# 🔄 Live Data Refresh Logic Explained

## 📊 Original Architecture (Flask + Continuous Processing)

### **How It Worked:**

```
┌─────────────────────────────────────────────────────────────────┐
│                     OLD SYSTEM (Flask)                          │
└─────────────────────────────────────────────────────────────────┘

[run_live.py - Background Process]
    │
    │ While True:
    │   1. Read Historical.xlsx from disk
    │   2. Read Live.xlsx from disk
    │   3. Process 204 stocks
    │   4. Write JSON files to disk
    │   5. Sleep 6 seconds
    │   6. Repeat forever ♾️
    │
    ↓
[processed/ folder]
    │
    │ - all_stocks.json
    │ - RELIANCE.json
    │ - TCS.json
    │ - ... (204 files)
    │
    ↓
[Flask app.py]
    │
    │ GET /summary/RELIANCE
    │   → Read RELIANCE.json from disk
    │   → Return JSON
    │
    ↓
[Frontend - index.html]
    │
    │ setInterval(loadStocks, 15000)
    │   → Call API every 15 seconds
    │   → Update UI with latest data
```

### **Key Points:**

1. **Continuous Processing** ✅
   - `run_live.py` runs in background 24/7
   - Re-processes Excel files every 6 seconds
   - Writes 204+ JSON files to disk every 6 seconds
   - High CPU and disk I/O usage

2. **Frontend Auto-Refresh** ✅
   - JavaScript `setInterval(loadStocks, 15000)`
   - Calls API every 15 seconds to fetch latest data
   - Updates dashboard automatically

3. **Data Flow:**
   ```
   Excel Files → run_live.py (every 6s) → JSON Files → Flask API → Frontend (every 15s)
   ```

4. **Why 6 seconds?**
   - Market data updates frequently during trading hours
   - 6 seconds is fast enough to catch most price/OI changes
   - Balances freshness vs CPU usage

5. **Why 15 seconds on frontend?**
   - Don't need to update UI every 6 seconds (too fast for users)
   - 15 seconds is smooth for dashboard viewing
   - Reduces network requests

---

## 🚀 New Architecture (FastAPI + On-Demand Processing)

### **How It Works Now:**

```
┌─────────────────────────────────────────────────────────────────┐
│                   NEW SYSTEM (FastAPI)                          │
└─────────────────────────────────────────────────────────────────┘

[Manual Trigger or Scheduled Task]
    │
    │ POST /api/v1/process/refresh
    │
    ↓
[DataProcessorService]
    │
    │ 1. Read Historical.xlsx from disk
    │ 2. Read Live.xlsx from disk
    │ 3. Process 204 stocks
    │ 4. Insert into SQLite database
    │ 5. Return status
    │
    ↓
[SQLite Database]
    │
    │ - historical_data table
    │ - live_data table
    │ - processing_metadata table
    │
    ↓
[FastAPI Endpoints]
    │
    │ GET /api/v1/stocks/RELIANCE
    │   → Query SQLite database
    │   → Return JSON
    │
    ↓
[Frontend - index.html]
    │
    │ setInterval(loadStocks, 15000)
    │   → Call API every 15 seconds
    │   → Update UI with latest data
```

### **Key Changes:**

1. **On-Demand Processing** 🆕
   - No background loop running 24/7
   - Processing triggered via API call
   - Lower CPU usage (only when triggered)

2. **Database Storage** 🆕
   - SQLite instead of JSON files
   - Faster queries
   - Better concurrency
   - Easier to scale

3. **Frontend Auto-Refresh** ✅ (Same as before)
   - Still uses `setInterval(loadStocks, 15000)`
   - Calls API every 15 seconds
   - Updates dashboard automatically

---

## 🔄 How to Handle Live Market Data Changes

### **Problem:**
Market data (prices, OI) changes every second during trading hours. But your data is stored in SQLite, which is static until you re-process.

### **Solution Options:**

---

### **Option 1: Manual Refresh (Current Implementation)**

**When to use:** Development, testing, or when you manually update Excel files

**How:**
```bash
# Manually trigger processing when you have new Excel files
curl -X POST 'http://127.0.0.1:9000/api/v1/process/refresh'
```

**Pros:**
- ✅ Low CPU usage
- ✅ Full control over when processing happens
- ✅ No continuous background tasks

**Cons:**
- ❌ Data becomes stale unless you trigger refresh
- ❌ Requires manual intervention

---

### **Option 2: Scheduled Background Task (Recommended)**

**When to use:** Production, when you want automatic updates

**Implementation:**

Create `background_processor.py`:
```python
import asyncio
from datetime import datetime, time
from app.services.data_processor import DataProcessorService

async def background_processor():
    """Background task that processes Excel files every 6 seconds"""
    processor = DataProcessorService()
    
    while True:
        try:
            # Check if market is open (9:15 AM - 3:30 PM IST)
            now = datetime.now().time()
            market_open = time(9, 15)
            market_close = time(15, 30)
            
            if market_open <= now <= market_close:
                # Market is open - process every 6 seconds
                print(f"[{datetime.now():%H:%M:%S}] Processing stocks...")
                result = processor.process_all_stocks(clear_existing=True)
                print(f"   ✅ {result['stocks_processed']}/{result['total_stocks']} stocks updated")
                await asyncio.sleep(6)  # Wait 6 seconds
            else:
                # Market is closed - check every 5 minutes
                print(f"[{datetime.now():%H:%M:%S}] Market closed. Sleeping...")
                await asyncio.sleep(300)  # Wait 5 minutes
                
        except Exception as e:
            print(f"❌ Background processor error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error
```

Update `main.py`:
```python
from fastapi import FastAPI
import asyncio
from background_processor import background_processor

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Start background processing when server starts"""
    asyncio.create_task(background_processor())
    print("🚀 Background processor started")

# ... rest of your routes
```

**Pros:**
- ✅ Automatic updates (same as old system)
- ✅ Data stays fresh
- ✅ Smart scheduling (only during market hours)
- ✅ Frontend auto-refresh works perfectly

**Cons:**
- ⚠️ Higher CPU usage (but still better than old system)

---

### **Option 3: Webhook/API Triggered (Advanced)**

**When to use:** When you have an external data provider that pushes updates

**How:**
```python
@router.post("/process/webhook")
async def process_webhook(data: dict, background_tasks: BackgroundTasks):
    """
    External system calls this when new Excel files are ready
    """
    background_tasks.add_task(processor.process_all_stocks)
    return {"status": "processing_started"}
```

---

### **Option 4: File Watcher (Automatic)**

**When to use:** When Excel files are automatically updated by another system

**Implementation:**

Install `watchdog`:
```bash
pip install watchdog
```

Create `file_watcher.py`:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.data_processor import DataProcessorService

class ExcelFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.processor = DataProcessorService()
        self.processing = False
    
    def on_modified(self, event):
        """Trigger processing when Excel files change"""
        if event.src_path.endswith(('.xlsx', '.xls')) and not self.processing:
            print(f"📂 File changed: {event.src_path}")
            self.processing = True
            try:
                result = self.processor.process_all_stocks()
                print(f"   ✅ Processed: {result['stocks_processed']} stocks")
            finally:
                self.processing = False

# Start watching
observer = Observer()
observer.schedule(ExcelFileHandler(), path="./live_data", recursive=False)
observer.start()
```

**Pros:**
- ✅ Fully automatic
- ✅ Only processes when files actually change
- ✅ Most efficient

**Cons:**
- ⚠️ Requires watchdog library
- ⚠️ More complex setup

---

## 🎯 Recommended Setup for Production

### **During Market Hours (9:15 AM - 3:30 PM):**

Use **Option 2** (Scheduled Background Task) with:
- ✅ Process every **6 seconds** (same as old system)
- ✅ Frontend auto-refresh every **15 seconds** (already implemented)
- ✅ Smart scheduling (only during market hours)

### **After Market Hours:**

- ✅ Process once when market closes (final snapshot)
- ✅ No processing during night (save CPU)
- ✅ Frontend still works (shows last processed data)

---

## 📊 Comparison: Old vs New

| Feature | Old (Flask) | New (FastAPI) |
|---------|-------------|---------------|
| **Data Storage** | JSON files (204+ files) | SQLite database |
| **Processing** | Continuous (every 6s) | On-demand or scheduled |
| **CPU Usage** | High (always running) | Low (only when needed) |
| **Disk I/O** | High (writes 204 files/6s) | Low (single DB file) |
| **Frontend Refresh** | Yes (15s) | Yes (15s) |
| **Concurrency** | Poor (file locking) | Excellent (SQLite) |
| **Scalability** | Limited | Better |
| **Data Freshness** | 6 seconds | 6 seconds (if using Option 2) |

---

## 🔍 Why Frontend Refreshes Every 15 Seconds

### **The Logic:**

```javascript
// In templates/index.html
async function loadStocks() {
  // 1. Fetch all stocks list
  const response = await fetch('/api/v1/stocks');
  const data = await response.json();
  
  // 2. Update UI with latest data from database
  renderStocks(data);
}

// 3. Call loadStocks every 15 seconds
setInterval(loadStocks, 15000);
loadStocks(); // Initial load
```

### **What Happens:**

```
T=0s    → Frontend loads page
          → Calls API, gets data from SQLite
          → Displays on dashboard

T=15s   → setInterval triggers
          → Calls API again
          → Gets data from SQLite (might be same as before)
          → Updates dashboard

T=30s   → setInterval triggers again
          → Calls API
          → Gets data from SQLite
          → Updates dashboard

... and so on every 15 seconds
```

### **Key Point:**

**Frontend refreshes every 15 seconds**, but **the data in SQLite only changes when you trigger processing**.

So you have two refresh cycles:
1. **Data refresh** (backend) → When you call `/process/refresh` or use background task
2. **UI refresh** (frontend) → Every 15 seconds automatically

---

## ✅ Recommended Implementation

For production use, implement **Option 2** (Background Task):

1. **Create `background_processor.py`** (code provided above)
2. **Update `main.py`** to start background task
3. **Configure market hours** (9:15 AM - 3:30 PM IST)
4. **Set processing interval** to 6 seconds

This gives you:
- ✅ Same refresh behavior as old system
- ✅ Better performance (SQLite vs JSON)
- ✅ Lower disk I/O
- ✅ Smart scheduling (market hours only)
- ✅ Frontend auto-refresh works perfectly

---

## 🎓 Summary

### **Old System:**
```
run_live.py (background) → Process every 6s → Write JSON → Flask API → Frontend (15s)
```

### **New System (Current):**
```
Manual trigger → Process → SQLite → FastAPI → Frontend (15s)
```

### **New System (Recommended):**
```
Background task (6s) → Process → SQLite → FastAPI → Frontend (15s)
```

---

## 🚀 Next Steps

**Choose your refresh strategy:**

1. **For Development:** Use manual refresh (current implementation)
   ```bash
   curl -X POST 'http://127.0.0.1:9000/api/v1/process/refresh'
   ```

2. **For Production:** Implement background task (Option 2)
   - See code examples above
   - Smart market hours detection
   - Same 6-second refresh as old system

3. **For Advanced:** Use file watcher (Option 4)
   - Automatic processing on file changes
   - Most efficient approach

---

**The frontend already has auto-refresh (15s) implemented!** ✅

You just need to decide how to keep the **database** updated (backend processing frequency).
