# ⚡ Quick Start - Optimized Version

## What Changed?

**Before:** Flask app processed 220 stocks every 6 seconds (high CPU usage)
**Now:** FastAPI with on-demand processing via upload API (zero CPU when idle)

---

## 🚀 Getting Started (3 Steps)

### Step 1: Start the Server

```bash
cd /media/rokkun09/271fcf58-e03d-46d8-a9cd-3425ed858c65/kk/fastapi_architecture
python main.py
```

Server starts at: **http://localhost:8000**

---

### Step 2: Upload Your Excel Files

#### Option A: Using Test Script (Easiest)

```bash
python test_upload.py /path/to/Historical.xlsx /path/to/Live.xlsx
```

#### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/api/v1/upload/excel-files" \
  -F "historical_file=@Historical.xlsx" \
  -F "live_file=@Live.xlsx"
```

#### Option C: Using Browser (API Docs)

1. Go to: http://localhost:8000/api/docs
2. Find `POST /api/v1/upload/excel-files`
3. Click "Try it out"
4. Upload both files
5. Click "Execute"

---

### Step 3: View Dashboard

Open browser: **http://localhost:8000**

Your data is now loaded! ✅

---

## 📝 Important Notes

### ✅ What Works:
- Dashboard shows all 220 stocks
- Historical and live data tables
- Favorites (saved in browser)
- Auto-refresh every 15 seconds (reads from SQLite, very fast)

### 🔄 How to Update Data:
1. Get new Historical.xlsx and Live.xlsx files
2. Upload via API (Step 2 above)
3. Old files are deleted, new ones replace them
4. Database is cleared and repopulated
5. Dashboard auto-refreshes

### 💾 Where is Data Stored:
- **Excel files**: `live_data/Historical.xlsx` and `live_data/Live.xlsx`
- **Database**: `options_data.db` (SQLite file in project root)

---

## 🎯 Common Tasks

### Check Processing Status:
```bash
curl http://localhost:8000/api/v1/upload/status
```

### Reprocess Existing Files:
```bash
curl -X POST http://localhost:8000/api/v1/upload/process
```

### Clear Database:
```bash
curl -X DELETE http://localhost:8000/api/v1/upload/data
```

### View API Docs:
Open: http://localhost:8000/api/docs

---

## 🔧 Troubleshooting

### "Missing files" error:
- Make sure you uploaded both Historical.xlsx and Live.xlsx
- Check the `live_data/` directory

### "Connection refused":
- Make sure the server is running (`python main.py`)
- Check if port 8000 is available

### No data showing on dashboard:
- Upload files first via API
- Check upload status: `curl http://localhost:8000/api/v1/upload/status`

### Database errors:
- Delete `options_data.db` and restart server
- Upload files again

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **CPU (Idle)** | ~0% |
| **CPU (Processing)** | 40-60% for ~10-30 seconds |
| **Memory** | 50-100 MB |
| **API Response** | 5-20ms |
| **Processing Time** | 10-30 seconds for 220 stocks |

---

## 📚 More Info

- **Full Guide**: See `OPTIMIZATION_GUIDE.md`
- **API Docs**: http://localhost:8000/api/docs
- **Architecture**: See `ARCHITECTURE.md`

---

**That's it! No more continuous CPU usage! 🎉**
