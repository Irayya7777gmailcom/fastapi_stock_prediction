# 📊 Data Flow & Excel Files Explained

## 🔄 Complete Data Flow

### **Step 1: API Trigger**

When you call:
```bash
POST /api/v1/upload/excel-files
# OR
POST /api/v1/process/refresh
```

### **Step 2: Data Processor Service**

**File:** `app/services/data_processor.py`

```python
def process_all_stocks(self):
    # 1. Locate Excel files
    live_path = live_data_dir / "Live.xlsx"
    hist_path = live_data_dir / "Historical.xlsx"
    
    # 2. Clear old data from database
    db.clear_stock_data()
    
    # 3. Loop through all 204 stocks
    for stock in all_stocks:  # ["RELIANCE", "TCS", "INFY", ...]
        # Extract data from Excel files
        hist = extract_historical_table(hist_path, stock)
        live = extract_live_table(live_path, hist_path, stock)
        
        # Save to SQLite database
        db.bulk_insert_historical(stock, hist)
        db.bulk_insert_live(stock, live)
```

---

## 📁 Excel Files Explained

### **1. Historical.xlsx (Master Data)**

**Purpose:** Contains historical Open Interest (OI) data for all stocks.

**Structure:**
```
Sheet: 23.11.2025 (or latest date)

| Stock    | Category        | Strike | Prev_OI  | Latest_OI | Call_OI_Difference | Put_OI_Difference | LTP     | Additional_Strike |
|----------|-----------------|--------|----------|-----------|--------------------|--------------------|---------|-------------------|
| RELIANCE | Call Resistance | 3000   | 100,000  | 120,000   | 20,000             | -                  | 2950.50 | Yes               |
| RELIANCE | Call Resistance | 3100   | 80,000   | 95,000    | 15,000             | -                  | 2950.50 | No                |
| RELIANCE | Put Support     | 2900   | 90,000   | 110,000   | -                  | 20,000             | 2950.50 | Yes               |
| TCS      | Call Resistance | 4200   | 50,000   | 60,000    | 10,000             | -                  | 4150.30 | No                |
...
```

**What it contains:**
- **Stock**: Stock symbol (RELIANCE, TCS, INFY, etc.)
- **Category**: Call Resistance, Call Support, Put Resistance, Put Support
- **Strike**: Option strike price
- **Prev_OI**: Previous Open Interest
- **Latest_OI**: Latest Open Interest
- **Call_OI_Difference**: Change in Call OI
- **Put_OI_Difference**: Change in Put OI
- **LTP**: Last Traded Price of the stock
- **Additional_Strike**: Flag if this is a new/additional strike

**How it's processed:**
```python
def extract_historical_table(hist_path, stock):
    # 1. Read the latest sheet (by date)
    sheet_names = get_sheet_names(hist_path)
    latest_sheet = pick_latest_sheet(sheet_names)  # "23.11.2025"
    
    # 2. Read Excel into DataFrame
    df = pd.read_excel(hist_path, sheet_name=latest_sheet)
    
    # 3. Find the "Stock" column
    stock_col = find_column(df, pattern="stock|symbol|name")
    
    # 4. Filter rows for this stock
    df_filtered = df[df[stock_col].upper() == stock.upper()]
    
    # 5. Extract all rows for this stock
    result = []
    for row in df_filtered:
        result.append({
            "Stock": row["Stock"],
            "Category": row["Category"],
            "Strike": row["Strike"],
            "Prev_OI": format_number(row["Prev_OI"]),
            "Latest_OI": format_number(row["Latest_OI"]),
            ...
        })
    
    return result
```

---

### **2. Live.xlsx (Real-time Data)**

**Purpose:** Contains LIVE/REAL-TIME Open Interest data organized by sections.

**Structure:**
```
Sheet: 23.11.2025 (or today's date)

Section 1: OPT_RELIANCE
+------------------------------------------+
| Call Support                             |
| Label | Prev_OI | Strike | ... | ...    |
| R3    | 120,000 | 2900   | ... | ...    |
| R2    | 110,000 | 2950   | ... | ...    |
| R1    | 100,000 | 3000   | ... | ...    |
+------------------------------------------+
| Put Support                              |
| Label | Prev_OI | Strike | ... | ...    |
| S1    | 90,000  | 2850   | ... | ...    |
| S2    | 85,000  | 2800   | ... | ...    |
+------------------------------------------+
| Call Resistance                          |
| Label | Prev_OI | Strike | ... | ...    |
| R1    | 130,000 | 3050   | ... | ...    |
| R2    | 140,000 | 3100   | ... | ...    |
+------------------------------------------+
| Put Resistance                           |
| Label | Prev_OI | Strike | ... | ...    |
| S3    | 95,000  | 2750   | ... | ...    |
+------------------------------------------+

Section 2: OPT_TCS
... (similar structure)
```

**What it contains:**
- **Sections per stock**: Each stock has its own section (OPT_RELIANCE, OPT_TCS, etc.)
- **4 subsections**: Call Support, Put Support, Call Resistance, Put Resistance
- **Label**: Support/Resistance level (S1, S2, R1, R2, etc.)
- **Prev_OI**: Previous Open Interest
- **Strike**: Option strike price
- **OI_Diff**: Difference from historical data
- **Is_NewStrike**: Flag if this strike is new
- **Add_Strike**: Additional strike marker

**How it's processed:**
```python
def extract_live_table(live_path, hist_path, stock):
    # 1. First, get historical data for comparison
    hist_data = extract_historical_table(hist_path, stock)
    
    # Build maps for comparison
    call_map = {}  # {strike: latest_oi}
    put_map = {}   # {strike: latest_oi}
    for row in hist_data:
        if "call" in row["Category"].lower():
            call_map[row["Strike"]] = row["Latest_OI"]
        if "put" in row["Category"].lower():
            put_map[row["Strike"]] = row["Latest_OI"]
    
    # 2. Read live data (today's sheet)
    sheet_names = get_sheet_names(live_path)
    today_sheet = pick_latest_sheet(sheet_names, target_date=today)
    
    # 3. Read entire sheet without header (unstructured data)
    df = pd.read_excel(live_path, sheet_name=today_sheet, header=None)
    
    # 4. Find the stock's section (OPT_RELIANCE)
    start_idx = find_line_with_pattern(df, f"OPT_{stock}")
    end_idx = find_next_opt_section(df, start_idx)
    
    # 5. Extract the block for this stock
    stock_block = df[start_idx:end_idx]
    
    # 6. Parse the 4 sections (Call Support, Put Support, etc.)
    sections = {}
    for i, line in enumerate(stock_block):
        if "call support" in line.lower():
            sections["Call Support"] = i
        if "put support" in line.lower():
            sections["Put Support"] = i
        if "call resistance" in line.lower():
            sections["Call Resistance"] = i
        if "put resistance" in line.lower():
            sections["Put Resistance"] = i
    
    # 7. Extract data from each section
    result = []
    for section_name, section_idx in sections.items():
        # Get rows after the section header
        for row in stock_block[section_idx + 1:]:
            if is_empty_or_new_section(row):
                break
            
            # Parse the row data
            label = row[0]  # S1, R1, etc.
            prev_oi = row[1]
            strike = row[2]
            
            # Calculate OI difference from historical data
            hist_oi = call_map.get(strike, 0) if "call" in section_name.lower() else put_map.get(strike, 0)
            oi_diff = prev_oi - hist_oi
            
            # Check if this is a new strike
            is_new_strike = "Yes" if strike not in call_map and strike not in put_map else ""
            
            result.append({
                "Stock": stock,
                "Section": section_name,
                "Label": label,
                "Prev_OI": format_number(prev_oi),
                "Strike": strike,
                "OI_Diff": format_number(oi_diff),
                "Is_NewStrike": is_new_strike,
                "Add_Strike": get_additional_strike_flag(strike)
            })
    
    return result
```

---

## 🔗 How They Work Together

### **Historical.xlsx = BASELINE DATA**
- Contains the "master" OI data
- Organized by stock and category
- Easy to query: "Give me all RELIANCE data"

### **Live.xlsx = LIVE UPDATES**
- Contains real-time OI changes
- Organized by sections/levels (R1, R2, S1, S2)
- Unstructured format (requires complex parsing)

### **Relationship:**
```
Live Data = Real-time values
Historical Data = Reference values

OI Difference = Live.Prev_OI - Historical.Latest_OI
```

**Example:**
```
Historical.xlsx:
RELIANCE | Call Resistance | 3000 | Latest_OI: 120,000

Live.xlsx:
RELIANCE | Call Resistance | R1 | Prev_OI: 135,000 | Strike: 3000

OI Difference = 135,000 - 120,000 = +15,000 (Bullish)
```

---

## 📈 Dashboard Display

### **Historical Data Table:**
Shows the baseline OI data:
```
Stock    | Category        | Strike | Prev_OI  | Latest_OI | Call_OI_Diff | Put_OI_Diff
---------|-----------------|--------|----------|-----------|--------------|-------------
RELIANCE | Call Resistance | 3000   | 100,000  | 120,000   | +20,000      | -
RELIANCE | Put Support     | 2900   | 90,000   | 110,000   | -            | +20,000
```

### **Live Data Table:**
Shows real-time support/resistance levels:
```
Stock    | Section         | Label | Prev_OI  | Strike | OI_Diff  | New Strike
---------|-----------------|-------|----------|--------|----------|------------
RELIANCE | Call Resistance | R1    | 135,000  | 3000   | +15,000  | No
RELIANCE | Call Resistance | R2    | 140,000  | 3100   | +10,000  | Yes
RELIANCE | Put Support     | S1    | 95,000   | 2900   | +5,000   | No
```

---

## 🎯 Why Both Files?

### **Historical.xlsx:**
- ✅ Clean, structured data
- ✅ Easy to query
- ✅ Provides baseline OI values
- ✅ Shows historical trends

### **Live.xlsx:**
- ✅ Real-time data
- ✅ Support/Resistance levels (R1, R2, S1, S2)
- ✅ Shows market sentiment
- ✅ Identifies new strikes
- ⚠️ Unstructured format (harder to parse)

**Together:** They provide complete options analysis:
- Historical = "What was the OI?"
- Live = "What is the OI now?"
- Difference = "How did it change?" (Bullish/Bearish indicator)

---

## 🔍 Data Flow Summary

```
1. Excel Files (Historical.xlsx + Live.xlsx)
   ↓
2. ExcelUtils.extract_historical_table()
   - Reads Historical.xlsx
   - Filters by stock
   - Extracts baseline OI data
   ↓
3. ExcelUtils.extract_live_table()
   - Reads Live.xlsx
   - Parses unstructured sections
   - Compares with historical data
   - Calculates OI differences
   ↓
4. DataProcessor.process_all_stocks()
   - Loops through 204 stocks
   - Calls extract functions for each
   ↓
5. Database (SQLAlchemy)
   - Bulk insert historical data
   - Bulk insert live data
   ↓
6. API Response
   - Returns success/failure
   - Shows stocks processed count
   ↓
7. Dashboard
   - Reads from SQLite database
   - Displays both tables
   - Auto-refreshes every 15s
```

---

## 🐛 Common Issues & Solutions

### Issue: "header must be integer or list of integers"
**Cause:** Pandas updated, `header='infer'` is deprecated

**Solution:** ✅ Fixed by changing to `header=0`

### Issue: "Stock not found in Excel"
**Cause:** Stock name mismatch or Excel structure changed

**Solution:** Check Excel file format and stock names

### Issue: "No data extracted"
**Cause:** Sheet name doesn't match date format

**Solution:** Check sheet names in Excel files

---

## 📝 Key Takeaways

1. **Historical.xlsx** = Structured baseline OI data
2. **Live.xlsx** = Unstructured real-time OI data with support/resistance levels
3. **Both files are required** for complete options analysis
4. **OI Difference** = Most important metric (shows bullish/bearish sentiment)
5. **Processing happens on-demand** via API (not continuous)
6. **Data stored in SQLite** for fast dashboard queries

---

## 🎓 Understanding OI (Open Interest)

**Open Interest** = Total number of outstanding option contracts

**Call OI Increase** = Bullish (buyers adding positions)
**Put OI Increase** = Bearish (buyers adding positions)

**Example:**
```
RELIANCE at 2950

Call 3000: OI increased by 20,000
→ Traders betting price will go above 3000 (Bullish)

Put 2900: OI increased by 15,000
→ Traders betting price won't fall below 2900 (Support)
```

**Dashboard helps traders:**
- Identify strong support/resistance levels
- Detect new strike additions (new interest areas)
- Track OI changes (sentiment shifts)
- Make informed trading decisions

---

**Now restart the server and try the API again! The error is fixed.** 🚀
