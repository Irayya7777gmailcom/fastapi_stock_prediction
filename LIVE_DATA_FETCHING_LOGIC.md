# 🔍 Live Data Fetching & Storage Logic - Complete Flow

## ❓ Your Question Answered

> **"Where is the core logic of fetching live data and storing in DB? Is it using third-party API or URL?"**

**Answer:** ❌ **NO third-party API or URL**

**It's reading from LOCAL EXCEL FILES** that you provide:
- `Historical.xlsx` - Baseline OI data
- `Live.xlsx` - Real-time OI data with support/resistance levels

---

## 🎯 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA SOURCE                                  │
│                                                                 │
│  Your Local Folder: live_data/                                 │
│  ├── Historical.xlsx  (baseline OI data)                        │
│  └── Live.xlsx        (real-time OI data)                       │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: FETCH FROM EXCEL                           │
│                                                                 │
│  File: app/services/excel_utils.py                             │
│  Class: ExcelUtils                                             │
│                                                                 │
│  Methods:                                                       │
│  - safe_read_excel()           → Read Excel file               │
│  - extract_historical_table()  → Parse Historical.xlsx         │
│  - extract_live_table()        → Parse Live.xlsx               │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 2: PROCESS DATA                               │
│                                                                 │
│  File: app/services/data_processor.py                          │
│  Class: DataProcessorService                                   │
│                                                                 │
│  Methods:                                                       │
│  - process_all_stocks()    → Process 204 stocks                │
│  - process_single_stock()  → Process one stock                 │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 3: STORE IN DATABASE                          │
│                                                                 │
│  File: app/core/database_sqlalchemy.py                         │
│  Class: Database                                               │
│                                                                 │
│  Methods:                                                       │
│  - bulk_insert_historical()  → Store historical data           │
│  - bulk_insert_live()        → Store live data                 │
│  - log_processing()          → Log operation                   │
│                                                                 │
│  Database: SQLite (options_data.db)                            │
│  Tables:                                                        │
│  - historical_data (baseline OI)                               │
│  - live_data (real-time OI)                                    │
│  - processing_metadata (audit log)                             │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 4: API ENDPOINTS                              │
│                                                                 │
│  File: app/api/v1/endpoints/stocks.py                          │
│                                                                 │
│  Endpoints:                                                     │
│  GET /api/v1/stocks/{stock}  → Fetch from SQLite               │
│  GET /api/v1/stocks          → All stocks                      │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              STEP 5: FRONTEND DISPLAY                           │
│                                                                 │
│  File: templates/index.html                                    │
│                                                                 │
│  JavaScript:                                                    │
│  - Fetch from API every 15 seconds                             │
│  - Display on dashboard                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Detailed Step-by-Step Flow

### **STEP 1: Fetch from Excel Files**

**File:** `app/services/excel_utils.py`

#### **1.1 Read Excel File (No Locking)**

```python
@staticmethod
def safe_read_excel(path: Path, sheet_name=None, header=0, engine="openpyxl"):
    """Read Excel file without locking"""
    with open(path, "rb") as f:
        return pd.read_excel(
            BytesIO(f.read()),           # Read into memory
            sheet_name=sheet_name,
            header=header,
            dtype=str,                   # All as strings
            engine=engine
        ).fillna("")
```

**Key Points:**
- ✅ Reads entire file into memory (BytesIO)
- ✅ No file locking (can read while Excel is open)
- ✅ Uses openpyxl engine (handles .xlsx format)
- ✅ Converts all data to strings

---

#### **1.2 Extract Historical Data**

**Method:** `extract_historical_table(hist_path, stock)`

**Logic:**

```python
def extract_historical_table(self, hist_path: Path, stock: str):
    """Extract historical data"""
    
    # 1. Get sheet names from Historical.xlsx
    sheet_names = self.safe_read_excel_sheetnames(hist_path)
    
    # 2. Pick latest sheet (by date: "23.11.2025")
    sheet = self.pick_latest_sheet(sheet_names)
    
    # 3. Read the sheet
    df = self.safe_read_excel(hist_path, sheet_name=sheet)
    
    # 4. Find "Stock" column (flexible naming)
    stock_col = next((c for c in df.columns 
                     if re.search(r"stock|symbol|name", c, re.I)), None)
    
    # 5. Filter rows for this stock
    df["__clean"] = df[stock_col].str.upper().str.strip()\
                                  .apply(lambda x: re.sub(r'\W+', '', x))
    
    if stock.upper() not in df["__clean"].values:
        return []  # Stock not found
    
    # 6. Extract relevant columns
    data = df[df["__clean"] == stock.upper()].copy()
    
    # 7. Format and return
    result = []
    for _, r in data.iterrows():
        row = {
            "Stock": stock,
            "Category": r.get("Category", ""),
            "Strike": r.get("Strike", ""),
            "Prev_OI": format_number(r.get("Prev_OI", "")),
            "Latest_OI": format_number(r.get("Latest_OI", "")),
            "Call_OI_Difference": format_number(r.get("Call_OI_Difference", "")),
            "Put_OI_Difference": format_number(r.get("Put_OI_Difference", "")),
            "LTP": r.get("LTP", ""),
            "Additional_Strike": r.get("Additional_Strike", "")
        }
        result.append(row)
    
    return result
```

**Output Example:**
```python
[
    {
        "Stock": "RELIANCE",
        "Category": "Call Resistance",
        "Strike": "3000",
        "Prev_OI": "100,000",
        "Latest_OI": "120,000",
        "Call_OI_Difference": "20,000",
        "Put_OI_Difference": "",
        "LTP": "2950.50",
        "Additional_Strike": "Yes"
    },
    {
        "Stock": "RELIANCE",
        "Category": "Put Support",
        "Strike": "2900",
        ...
    }
]
```

---

#### **1.3 Extract Live Data**

**Method:** `extract_live_table(live_path, hist_path, stock)`

**Logic:**

```python
def extract_live_table(self, live_path: Path, hist_path: Path, stock: str):
    """Extract live data from Live.xlsx"""
    
    # ===== PART 1: Build comparison maps from Historical.xlsx =====
    
    # Read historical data
    df1 = self.safe_read_excel(hist_path, sheet_name=latest_sheet)
    
    # Build maps for OI comparison
    call_map = {}  # {strike: latest_oi}
    put_map = {}   # {strike: latest_oi}
    
    for _, r in df1.iterrows():
        strike_key = self.strike_key(r.get("Strike", ""))
        oi_value = self.to_number(r.get("Latest_OI", ""))
        category = str(r.get("Category", "")).lower()
        
        if "call" in category and oi_value is not None:
            call_map[strike_key] = oi_value
        if "put" in category and oi_value is not None:
            put_map[strike_key] = oi_value
    
    # ===== PART 2: Parse Live.xlsx unstructured data =====
    
    # Read live data (no header - unstructured)
    raw = self.safe_read_excel(live_path, sheet_name=chosen, header=None)
    
    # Convert to text for pattern matching
    texts = [" ".join([str(x).strip() for x in row if str(x).strip()]) 
             for row in raw.values]
    
    # Find stock section (e.g., "OPT_RELIANCE")
    start_idx = self._find_live_block_start(texts, stock_norm)
    
    if start_idx is None:
        return []  # Stock not found in live data
    
    # Find end of stock section (next OPT_STOCK)
    end_idx = next((j for j in range(start_idx + 1, len(texts))
                   if re.search(r'^\s*OPT[_\-\s]?[A-Za-z0-9]+', texts[j], re.I)), 
                   len(texts))
    
    block = raw.iloc[start_idx:end_idx].reset_index(drop=True)
    
    # ===== PART 3: Parse 4 sections =====
    
    sections = {}
    for i in range(len(block)):
        line = " ".join([str(x).strip() for x in block.iloc[i]])
        tl = line.lower()
        
        if 'call support' in tl:
            sections['Call Support'] = i
        if 'put support' in tl:
            sections['Put Support'] = i
        if 'call resistance' in tl:
            sections['Call Resistance'] = i
        if 'put resistance' in tl:
            sections['Put Resistance'] = i
    
    # ===== PART 4: Extract data from each section =====
    
    result = []
    for sec_name, sec_idx in sections.items():
        for r in range(sec_idx + 1, len(block)):
            row_vals = [str(x).strip() for x in block.iloc[r]]
            
            # Skip empty rows
            if all(v == "" for v in row_vals):
                break
            
            # Skip if new section starts
            if any(h in " ".join(row_vals).lower() for h in 
                  ('call support', 'put support', 'call resistance', 'put resistance')):
                break
            
            # Extract data based on section
            if "call" in sec_name.lower():
                label, prev_oi, strike = row_vals[0], row_vals[1], row_vals[2]
            else:
                label, prev_oi, strike = row_vals[6], row_vals[7], row_vals[8]
            
            # Calculate OI difference
            prev_num = self.to_number(prev_oi)
            sk = self.strike_key(strike)
            oi_diff = ""
            
            if prev_num is not None:
                base = call_map.get(sk, 0) if "call" in sec_name.lower() else put_map.get(sk, 0)
                oi_diff = self.format_number(prev_num - base)
            
            result.append({
                "Section": sec_name,
                "Label": label,
                "Prev_OI": self.format_number(prev_num),
                "Strike": strike,
                "Stock": stock,
                "OI_Diff": oi_diff,
                "Is_NewStrike": "Yes" if sk not in all_strikes else "",
                "Add_Strike": add_map.get(sk, "")
            })
    
    return result
```

**Output Example:**
```python
[
    {
        "Section": "Call Resistance",
        "Label": "R1",
        "Prev_OI": "135,000",
        "Strike": "3000",
        "Stock": "RELIANCE",
        "OI_Diff": "+15,000",      # Calculated: 135,000 - 120,000
        "Is_NewStrike": "",
        "Add_Strike": "Yes"
    },
    {
        "Section": "Call Resistance",
        "Label": "R2",
        "Prev_OI": "140,000",
        "Strike": "3100",
        "Stock": "RELIANCE",
        "OI_Diff": "+10,000",
        "Is_NewStrike": "Yes",     # New strike not in historical
        "Add_Strike": ""
    }
]
```

---

### **STEP 2: Process Data**

**File:** `app/services/data_processor.py`

**Class:** `DataProcessorService`

```python
def process_all_stocks(self, clear_existing=True):
    """Process all stocks and save to SQLite database"""
    
    # 1. Get file paths
    live_path = self.live_data_dir / self.live_file      # Live.xlsx
    hist_path = self.live_data_dir / self.hist_file      # Historical.xlsx
    
    # 2. Check files exist
    if not live_path.exists() or not hist_path.exists():
        return {"status": "error", "message": "Files not found"}
    
    # 3. Clear old data (optional)
    if clear_existing:
        db.clear_stock_data()
    
    # 4. Process each stock
    success = 0
    errors = []
    
    for stock in self.all_stocks:  # 204 stocks
        try:
            # Extract from Excel
            hist = self.utils.extract_historical_table(hist_path, stock)
            live = self.utils.extract_live_table(live_path, hist_path, stock)
            
            # Store in database
            if hist:
                db.bulk_insert_historical(stock, hist)
            
            if live:
                db.bulk_insert_live(stock, live)
            
            if hist or live:
                success += 1
                
        except Exception as e:
            errors.append(f"{stock}: {str(e)}")
            print(f"[ERROR] {stock}: {e}")
    
    # 5. Log the operation
    db.log_processing("full_process", success, "success", 
                      f"Processed {success}/{len(self.all_stocks)} stocks")
    
    return {
        "status": "success",
        "stocks_processed": success,
        "total_stocks": len(self.all_stocks),
        "errors": errors[:10]
    }
```

---

### **STEP 3: Store in Database**

**File:** `app/core/database_sqlalchemy.py`

**Class:** `Database`

#### **3.1 Bulk Insert Historical Data**

```python
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
        session.bulk_save_objects(objects)  # Optimized insert
```

**Database Table: `historical_data`**
```sql
CREATE TABLE historical_data (
    id INTEGER PRIMARY KEY,
    stock TEXT NOT NULL,
    category TEXT,
    strike TEXT,
    prev_oi TEXT,
    latest_oi TEXT,
    call_oi_difference TEXT,
    put_oi_difference TEXT,
    ltp TEXT,
    additional_strike TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

#### **3.2 Bulk Insert Live Data**

```python
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
        session.bulk_save_objects(objects)  # Optimized insert
```

**Database Table: `live_data`**
```sql
CREATE TABLE live_data (
    id INTEGER PRIMARY KEY,
    stock TEXT NOT NULL,
    section TEXT,
    label TEXT,
    prev_oi TEXT,
    strike TEXT,
    oi_diff TEXT,
    is_new_strike TEXT,
    add_strike TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

---

### **STEP 4: API Endpoints**

**File:** `app/api/v1/endpoints/stocks.py`

```python
@router.get("/{stock}", response_model=StockSummaryResponse)
async def get_stock_summary(stock: str = Path(...)):
    """Retrieve historical and live data for a specific stock"""
    try:
        summary = await stock_service.get_stock_summary(stock.upper())
        return summary
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Stock not found")
```

**Service Logic:**

```python
async def get_stock_summary(self, stock: str):
    """Get stock summary from database"""
    
    # Query database
    historical = db.get_historical_data(stock)
    live = db.get_live_data(stock)
    
    return StockSummaryResponse(
        stock=stock,
        historical=historical,
        live=live
    )
```

**API Response:**
```json
{
  "stock": "RELIANCE",
  "historical": [
    {
      "Stock": "RELIANCE",
      "Category": "Call Resistance",
      "Strike": "3000",
      "Prev_OI": "100,000",
      "Latest_OI": "120,000",
      "Call_OI_Difference": "20,000",
      "Put_OI_Difference": "",
      "LTP": "2950.50",
      "Additional_Strike": "Yes"
    }
  ],
  "live": [
    {
      "Section": "Call Resistance",
      "Label": "R1",
      "Prev_OI": "135,000",
      "Strike": "3000",
      "OI_Diff": "+15,000",
      "Is_NewStrike": "",
      "Add_Strike": "Yes"
    }
  ]
}
```

---

### **STEP 5: Frontend Display**

**File:** `templates/index.html`

```javascript
async function loadStocks() {
    // Fetch from API
    const response = await fetch('/api/v1/stocks/RELIANCE');
    const data = await response.json();
    
    // Display historical data
    displayHistoricalTable(data.historical);
    
    // Display live data
    displayLiveTable(data.live);
}

// Auto-refresh every 15 seconds
setInterval(loadStocks, 15000);
```

---

## 📊 Complete Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                             │
│                                                             │
│  live_data/                                                │
│  ├── Historical.xlsx  ← Baseline OI data                   │
│  └── Live.xlsx        ← Real-time OI data                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    (No API/URL)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              EXCEL READING (In-Memory)                      │
│                                                             │
│  app/services/excel_utils.py                               │
│  - safe_read_excel()                                       │
│  - extract_historical_table()                              │
│  - extract_live_table()                                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              DATA PROCESSING                                │
│                                                             │
│  app/services/data_processor.py                            │
│  - process_all_stocks()                                    │
│  - process_single_stock()                                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              DATABASE STORAGE                               │
│                                                             │
│  app/core/database_sqlalchemy.py                           │
│  - bulk_insert_historical()                                │
│  - bulk_insert_live()                                      │
│                                                             │
│  SQLite: options_data.db                                   │
│  Tables:                                                    │
│  - historical_data (baseline OI)                           │
│  - live_data (real-time OI)                                │
│  - processing_metadata (audit log)                         │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              API ENDPOINTS                                  │
│                                                             │
│  app/api/v1/endpoints/stocks.py                            │
│  GET /api/v1/stocks/{stock}                                │
│  GET /api/v1/stocks                                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              FRONTEND DISPLAY                               │
│                                                             │
│  templates/index.html                                      │
│  - Auto-refresh every 15 seconds                           │
│  - Display historical & live tables                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Points

### **1. NO Third-Party API**
- ❌ Not using any external API
- ❌ Not fetching from URL
- ✅ Reading from LOCAL Excel files

### **2. Data Source**
- **Historical.xlsx** - You provide this file
- **Live.xlsx** - You provide this file
- Both stored in `live_data/` folder

### **3. Processing Pipeline**
```
Excel Files → Parse → Extract → Format → Database → API → Frontend
```

### **4. Storage**
- Single SQLite file: `options_data.db`
- 3 main tables: historical_data, live_data, processing_metadata
- Fast queries, no file locking

### **5. Refresh Mechanism**
- Manual: Call `/api/v1/process/refresh`
- Automatic: Enable background processor (every 6 seconds)
- Frontend: Auto-refresh every 15 seconds

---

## 🎯 How to Trigger Processing

### **Option 1: Manual API Call**
```bash
curl -X POST 'http://127.0.0.1:9000/api/v1/process/refresh'
```

### **Option 2: Enable Background Processor**
```python
# In main.py
ENABLE_BACKGROUND_PROCESSOR = True
```

### **Option 3: Upload New Excel Files**
```bash
curl -X POST 'http://127.0.0.1:9000/api/v1/upload/excel-files' \
  -F "historical=@Historical.xlsx" \
  -F "live=@Live.xlsx"
```

---

## 📁 File Structure

```
fastapi_architecture/
├── app/
│   ├── services/
│   │   ├── excel_utils.py          ← Fetch from Excel
│   │   ├── data_processor.py        ← Process data
│   │   └── background_processor.py  ← Auto-refresh
│   ├── core/
│   │   └── database_sqlalchemy.py   ← Store in DB
│   ├── api/v1/endpoints/
│   │   └── stocks.py                ← API endpoints
│   └── models/
│       └── stock_models.py          ← Database models
├── live_data/
│   ├── Historical.xlsx              ← Data source
│   └── Live.xlsx                    ← Data source
├── options_data.db                  ← SQLite database
└── templates/
    └── index.html                   ← Frontend
```

---

## ✅ Summary

**Your system:**
1. ✅ Reads Excel files from local folder
2. ✅ Parses and extracts data
3. ✅ Stores in SQLite database
4. ✅ Serves via FastAPI endpoints
5. ✅ Displays on frontend

**NO external API or URL involved!**

Everything is local and self-contained. 🚀
