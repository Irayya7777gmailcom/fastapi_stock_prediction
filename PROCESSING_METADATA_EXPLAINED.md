# 📊 Processing Metadata Explained

## 🎯 What is `processing_metadata`?

The `processing_metadata` table is a **logging and audit trail** system that tracks every data processing operation in your application.

---

## 🔍 Purpose & Benefits

### **1. Audit Trail**
Track when and how data was processed:
```sql
SELECT * FROM processing_metadata ORDER BY processed_at DESC LIMIT 5;
```

**Example Output:**
```
id | process_type  | stocks_processed | status  | message                              | processed_at        
---|---------------|------------------|---------|--------------------------------------|---------------------
5  | full_process  | 106              | success | Processed 106/204 stocks successfully| 2025-11-23 14:22:13
4  | full_process  | 98               | success | Processed 98/204 stocks successfully | 2025-11-23 12:15:45
3  | single_stock  | 1                | success | Processed RELIANCE successfully      | 2025-11-23 11:30:22
2  | full_process  | 0                | error   | Missing files. Expected: Historical  | 2025-11-23 10:05:10
1  | full_process  | 204              | success | Processed 204/204 stocks successfully| 2025-11-23 09:00:00
```

### **2. Error Tracking**
Identify when processing fails:
```python
# If Excel files are missing or corrupted
db.log_processing("full_process", 0, "error", "Excel files not found")
```

### **3. Performance Monitoring**
Track processing efficiency over time:
- How many stocks processed each time?
- Success rate trends
- Processing frequency

### **4. API Response**
Provide processing history via API:
```bash
GET /api/v1/processing/history
```

**Response:**
```json
{
  "history": [
    {
      "process_type": "full_process",
      "stocks_processed": 106,
      "status": "success",
      "message": "Processed 106/204 stocks successfully",
      "processed_at": "2025-11-23T14:22:13"
    }
  ]
}
```

---

## 📋 Table Schema

```sql
CREATE TABLE processing_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process_type TEXT NOT NULL,        -- Type: 'full_process', 'single_stock', 'upload'
    stocks_processed INTEGER,          -- Number of stocks successfully processed
    status TEXT,                       -- 'success', 'error', 'partial'
    message TEXT,                      -- Human-readable status message
    processed_at TIMESTAMP NOT NULL,   -- When the processing occurred
    created_at DATETIME NOT NULL,      -- Record creation timestamp
    updated_at DATETIME NOT NULL       -- Last update timestamp
);
```

### **Column Descriptions:**

| Column | Type | Purpose |
|--------|------|---------|
| `id` | INTEGER | Unique identifier (auto-increment) |
| `process_type` | TEXT | Type of processing: `full_process`, `single_stock`, `upload` |
| `stocks_processed` | INTEGER | Count of successfully processed stocks |
| `status` | TEXT | Operation status: `success`, `error`, `partial` |
| `message` | TEXT | Detailed status message or error description |
| `processed_at` | TIMESTAMP | When the processing operation occurred |
| `created_at` | DATETIME | When this log entry was created (from BaseModel) |
| `updated_at` | DATETIME | Last update time (from BaseModel) |

---

## 🔄 How It Works

### **1. During Processing**

When you call the API:
```bash
POST /api/v1/process/refresh
```

The system logs the operation:
```python
# In data_processor.py
def process_all_stocks(self):
    success = 0
    
    # Process all stocks
    for stock in self.all_stocks:
        try:
            hist = extract_historical_table(hist_path, stock)
            live = extract_live_table(live_path, hist_path, stock)
            
            if hist or live:
                db.bulk_insert_historical(stock, hist)
                db.bulk_insert_live(stock, live)
                success += 1
        except Exception as e:
            print(f"Error processing {stock}: {e}")
    
    # Log the result
    status_msg = f"Processed {success}/{len(self.all_stocks)} stocks successfully"
    db.log_processing("full_process", success, "success", status_msg)
```

### **2. Logging Function**

In `database_sqlalchemy.py`:
```python
def log_processing(self, process_type: str, stocks_processed: int, 
                   status: str, message: str):
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
        session.commit()
```

### **3. Querying History**

In `stock_service.py`:
```python
def get_processing_history(self):
    """Get recent processing history"""
    with db.get_session() as session:
        history = session.query(ProcessingMetadata)\
                        .order_by(ProcessingMetadata.processed_at.desc())\
                        .limit(10)\
                        .all()
        return [h.to_dict() for h in history]
```

---

## 🎯 Use Cases

### **1. Dashboard Display**
Show last processing time and success rate:
```javascript
// Frontend Dashboard
fetch('/api/v1/processing/last')
  .then(res => res.json())
  .then(data => {
    document.getElementById('last-update').textContent = 
      `Last updated: ${data.processed_at} (${data.stocks_processed} stocks)`;
  });
```

### **2. Debugging**
Track down processing failures:
```sql
-- Find all failed processing attempts
SELECT * FROM processing_metadata 
WHERE status = 'error' 
ORDER BY processed_at DESC;
```

### **3. Performance Analysis**
```sql
-- Average stocks processed per run
SELECT AVG(stocks_processed) as avg_stocks,
       COUNT(*) as total_runs,
       SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_runs
FROM processing_metadata
WHERE process_type = 'full_process'
AND processed_at > datetime('now', '-7 days');
```

### **4. API Monitoring**
```python
# Health check endpoint
@router.get("/health")
async def health_check():
    last_process = db.get_last_processing()
    
    if not last_process:
        return {"status": "warning", "message": "No processing history"}
    
    if last_process.status == "error":
        return {"status": "error", "message": last_process.message}
    
    return {
        "status": "healthy",
        "last_process": last_process.processed_at,
        "stocks_processed": last_process.stocks_processed
    }
```

---

## 🐛 Why Only 106/204 Stocks Processed?

When you see:
```
Processed 106/204 stocks successfully
```

**Reasons:**

### **1. Stock Not in Excel Files**
Some stocks in `ALL_STOCKS` list may not have data in the Excel files:
- New stocks not yet added to Excel
- Delisted stocks still in the list
- Spelling/naming mismatches

**Example:**
```python
ALL_STOCKS = ["RELIANCE", "TCS", "NEWSTOCK123", ...]
```
If `NEWSTOCK123` doesn't exist in Excel:
```python
hist = extract_historical_table(hist_path, "NEWSTOCK123")  # Returns []
live = extract_live_table(live_path, hist_path, "NEWSTOCK123")  # Returns []

# Not counted in success (no data to insert)
```

### **2. Excel Sheet Structure Changed**
If Excel format changes:
- Column names renamed
- Sheet names changed
- Data layout modified

**Error Example:**
```
Historical error SAIL: header must be integer or list of integers
```
→ Pandas couldn't parse the Excel header row

### **3. Data Format Issues**
- Empty sheets for some stocks
- Corrupted data
- Missing required columns

---

## ✅ This is Normal Behavior!

**106/204 is acceptable** if:
- ✅ Data is being inserted for the stocks that do exist
- ✅ Dashboard displays data correctly
- ✅ No critical errors in logs

**Not all stocks need to be in the Excel files** - you may only trade/track a subset.

---

## 🔧 How to Investigate Missing Stocks

### **1. Check Which Stocks Failed**
```python
# In data_processor.py, the errors list shows details:
errors = []  # e.g., ["NEWSTOCK: No data found", "XYZ: Sheet not found"]
```

### **2. View Error Logs**
```bash
# Check terminal output when running:
POST /api/v1/process/refresh

# Look for lines like:
#   [ERROR] STOCKNAME: specific error message
```

### **3. Query Processing History**
```sql
-- Check recent processing attempts
SELECT process_type, stocks_processed, message, processed_at 
FROM processing_metadata 
ORDER BY processed_at DESC 
LIMIT 10;
```

### **4. Validate Excel Files**
```python
# Check which stocks exist in Excel:
import pandas as pd

# Historical.xlsx
df = pd.read_excel('live_data/Historical.xlsx', sheet_name='23.11.2025')
stocks_in_excel = df['Stock'].unique()
print(f"Found {len(stocks_in_excel)} stocks in Historical.xlsx")

# Compare with ALL_STOCKS
missing = set(ALL_STOCKS) - set(stocks_in_excel)
print(f"Missing stocks: {missing}")
```

---

## 🎓 Key Takeaways

1. **`processing_metadata` = Audit Log**
   - Tracks every processing operation
   - Records success/failure
   - Provides debugging information

2. **Why `created_at` and `updated_at`?**
   - Inherited from `BaseModel` (standard practice)
   - Tracks when log entry was created/modified
   - Useful for record versioning

3. **106/204 is OK**
   - Not all stocks need to exist in Excel
   - Focus on the ones that matter to you
   - Check logs to identify missing stocks

4. **Use for Monitoring**
   - Dashboard: Show last update time
   - API: Health check endpoints
   - Debugging: Track down processing failures

---

## 🚀 Future Enhancements

Possible features using `processing_metadata`:

1. **Email Alerts**
   ```python
   if processing.stocks_processed < 50:
       send_alert("Low processing count detected")
   ```

2. **Automated Retries**
   ```python
   last = db.get_last_processing()
   if last.status == "error":
       # Retry processing
       process_all_stocks()
   ```

3. **Performance Charts**
   ```javascript
   // Chart showing stocks processed over time
   const chartData = processingHistory.map(p => ({
       date: p.processed_at,
       count: p.stocks_processed
   }));
   ```

4. **Slack/Discord Notifications**
   ```python
   webhook_url = "https://hooks.slack.com/..."
   requests.post(webhook_url, json={
       "text": f"✅ Processed {stocks_processed} stocks successfully"
   })
   ```

---

**The `processing_metadata` table is your application's memory - it remembers everything!** 🧠
