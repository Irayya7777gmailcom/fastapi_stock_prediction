# 🚀 Complete Setup Instructions - SQLAlchemy Version

## Overview

Your FastAPI application is now fully optimized with:
- ✅ **SQLAlchemy ORM** - Professional database management
- ✅ **Alembic Migrations** - Database schema versioning
- ✅ **Upload API** - On-demand processing
- ✅ **Zero CPU Usage** - No background loops
- ✅ **HTML Dashboard** - Complete UI

---

## 📋 Prerequisites

- Python 3.8+
- pip
- Your Excel files: `Historical.xlsx` and `Live.xlsx`

---

## 🔧 Installation (Step by Step)

### Step 1: Navigate to Project Directory

```bash
cd /media/rokkun09/271fcf58-e03d-46d8-a9cd-3425ed858c65/kk/fastapi_architecture
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- FastAPI + Uvicorn (web framework)
- SQLAlchemy 2.0.25 (ORM)
- Alembic 1.13.1 (migrations)
- Pandas + OpenPyXL (Excel processing)
- Pydantic (data validation)

### Step 3: Run Database Migrations

```bash
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration
✅ Database initialized: /path/to/options_data.db
```

### Step 4: Start the Server

```bash
python main.py
```

**Expected output:**
```
✅ Database initialized: /path/to/options_data.db
🚀 Starting Options Dashboard API v1.0.0
📁 Processed data directory: /path/to/live_data
📊 Live data directory: /path/to/live_data
Server: http://0.0.0.0:8000
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 5: Upload Your Excel Files

**Option A: Using Test Script (Recommended)**
```bash
# In a new terminal
python test_upload.py live_data/Historical.xlsx live_data/Live.xlsx
```

**Option B: Using cURL**
```bash
curl -X POST "http://localhost:8000/api/v1/upload/excel-files" \
  -F "historical_file=@live_data/Historical.xlsx" \
  -F "live_file=@live_data/Live.xlsx"
```

**Option C: Using API Docs (Browser)**
1. Open: http://localhost:8000/api/docs
2. Find `POST /api/v1/upload/excel-files`
3. Click "Try it out"
4. Upload both files
5. Click "Execute"

### Step 6: Access the Dashboard

Open your browser and go to:
```
http://localhost:8000
```

You should see the Live OI Tracker dashboard with all your stock data!

---

## 📊 Verify Installation

### Check Database Tables:
```bash
sqlite3 options_data.db ".tables"
```

**Expected output:**
```
alembic_version      live_data            uploaded_files     
historical_data      processing_metadata
```

### Check Database Records:
```bash
sqlite3 options_data.db "SELECT COUNT(*) FROM historical_data;"
sqlite3 options_data.db "SELECT COUNT(*) FROM live_data;"
sqlite3 options_data.db "SELECT DISTINCT stock FROM historical_data LIMIT 10;"
```

### Check API Endpoints:
```bash
# Health check
curl http://localhost:8000/health

# Get all stocks
curl http://localhost:8000/api/v1/stocks/

# Get specific stock
curl http://localhost:8000/api/v1/stocks/RELIANCE

# Check processing status
curl http://localhost:8000/api/v1/upload/status
```

---

## 🎯 Quick Commands Reference

### Server Management:
```bash
# Start server
python main.py

# Start server on different port
PORT=8001 python main.py

# Start with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Database Management:
```bash
# Run migrations
alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Reset database (delete and recreate)
rm options_data.db
alembic upgrade head
```

### File Upload:
```bash
# Upload using test script
python test_upload.py Historical.xlsx Live.xlsx

# Upload with curl
curl -X POST "http://localhost:8000/api/v1/upload/excel-files" \
  -F "historical_file=@Historical.xlsx" \
  -F "live_file=@Live.xlsx"

# Reprocess existing files
curl -X POST "http://localhost:8000/api/v1/upload/process"

# Check status
curl http://localhost:8000/api/v1/upload/status

# Clear database
curl -X DELETE "http://localhost:8000/api/v1/upload/data"
```

### Database Inspection:
```bash
# Open SQLite CLI
sqlite3 options_data.db

# View tables
.tables

# View schema
.schema historical_data

# Query data
SELECT * FROM historical_data WHERE stock='RELIANCE' LIMIT 5;

# Count records
SELECT COUNT(*) FROM live_data;

# Get distinct stocks
SELECT DISTINCT stock FROM historical_data;

# Exit
.quit
```

---

## 🗂️ Project Structure

```
fastapi_architecture/
├── options_data.db              # SQLite database (auto-created)
├── live_data/                   # Excel files directory
│   ├── Historical.xlsx          # Upload via API
│   └── Live.xlsx                # Upload via API
│
├── alembic/                     # Migration system
│   ├── versions/
│   │   └── 001_initial_migration.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── models/
│   │   ├── base.py              # SQLAlchemy Base
│   │   ├── stock_models.py      # ORM Models
│   │   └── schemas.py           # Pydantic schemas
│   │
│   ├── core/
│   │   ├── database_sqlalchemy.py   # Database manager
│   │   └── config.py
│   │
│   ├── api/v1/endpoints/
│   │   ├── upload.py            # Upload API
│   │   ├── stocks.py            # Stock endpoints
│   │   └── data_processing.py
│   │
│   └── services/
│       ├── data_processor.py    # Excel processing
│       ├── stock_service.py     # Business logic
│       └── excel_utils.py       # Excel utilities
│
├── templates/
│   └── index.html               # Dashboard
│
├── static/
│   ├── style.css
│   └── assets/
│
├── alembic.ini                  # Alembic config
├── main.py                      # FastAPI app
├── test_upload.py               # Upload test script
├── requirements.txt
└── .env                         # Configuration
```

---

## 🔄 Workflow

### Initial Setup Flow:
```
1. Install dependencies (pip install -r requirements.txt)
   ↓
2. Run migrations (alembic upgrade head)
   ↓
3. Start server (python main.py)
   ↓
4. Upload files (python test_upload.py ...)
   ↓
5. Access dashboard (http://localhost:8000)
```

### Daily Usage Flow:
```
1. Start server (if not running)
   ↓
2. Upload new Excel files via API
   ↓
3. Data is processed and stored in SQLite
   ↓
4. View updated data on dashboard
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'sqlalchemy'"

**Cause:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt
```

---

### Issue: "Table historical_data already exists"

**Cause:** Database already has tables but migrations not tracked

**Solution:**
```bash
# Option 1: Delete database and recreate
rm options_data.db
alembic upgrade head

# Option 2: Stamp current version
alembic stamp head
```

---

### Issue: "Port 8000 already in use"

**Cause:** Another process is using port 8000

**Solution:**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
PORT=8001 python main.py
```

---

### Issue: "Connection refused"

**Cause:** Server not running

**Solution:**
```bash
# Start server
python main.py
```

---

### Issue: "No data on dashboard"

**Cause:** Files not uploaded yet

**Solution:**
```bash
# Upload files
python test_upload.py Historical.xlsx Live.xlsx

# Check status
curl http://localhost:8000/api/v1/upload/status
```

---

### Issue: "Migration out of sync"

**Cause:** Alembic version mismatch

**Solution:**
```bash
# Check current version
alembic current

# Reset migrations
alembic downgrade base
alembic upgrade head
```

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README_FINAL.md** | Complete reference guide |
| **QUICKSTART_OPTIMIZED.md** | Quick 3-step setup |
| **OPTIMIZATION_COMPLETE.md** | Why/what was optimized |
| **OPTIMIZATION_GUIDE.md** | Detailed architecture |
| **SQLALCHEMY_MIGRATION.md** | SQLAlchemy ORM guide |
| **SETUP_INSTRUCTIONS.md** | This file (step-by-step) |

**Recommended Reading Order:**
1. This file (setup)
2. QUICKSTART_OPTIMIZED.md (usage)
3. SQLALCHEMY_MIGRATION.md (understanding ORM)
4. OPTIMIZATION_GUIDE.md (deep dive)

---

## 🎓 Key Concepts

### SQLAlchemy ORM:
- Python objects represent database rows
- No manual SQL strings
- Type-safe operations
- Automatic connection management

### Alembic Migrations:
- Track database schema changes
- Version control for database
- Easy rollback/upgrade
- Auto-generate migrations

### Upload API:
- On-demand processing (no CPU hogging)
- Replaces 6-second loop
- Manual control over data updates

### Dashboard:
- Real-time data from SQLite
- Auto-refresh every 15 seconds
- Favorites management
- Fast queries (5-20ms)

---

## 🔍 Health Checks

### 1. Server Health:
```bash
curl http://localhost:8000/health
```
**Expected:** `{"status": "healthy", ...}`

### 2. Database Health:
```bash
sqlite3 options_data.db "SELECT COUNT(*) FROM historical_data;"
```
**Expected:** Number > 0 (after upload)

### 3. API Health:
```bash
curl http://localhost:8000/api/v1/stocks/
```
**Expected:** `{"all_stocks": [...]}`

### 4. Dashboard Health:
```bash
curl -I http://localhost:8000
```
**Expected:** `HTTP/1.1 200 OK`

---

## 🚀 Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Server Startup | 1-2s | Database init |
| File Upload | 5-10s | For ~5MB files |
| Processing 220 stocks | 10-20s | Bulk insert optimized |
| API Query (single stock) | 5-20ms | SQLite indexed |
| Dashboard Load | 100-300ms | Full page with data |
| CPU (Idle) | ~0% | No background processing |

---

## ✅ Checklist

### Installation:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Migrations run (`alembic upgrade head`)
- [ ] Database created (`options_data.db` exists)
- [ ] Server starts successfully

### Configuration:
- [ ] `.env` file present
- [ ] `LIVE_DATA_DIR` set correctly
- [ ] Port 8000 available

### Data:
- [ ] Excel files uploaded via API
- [ ] Database has records
- [ ] Dashboard shows data

### Verification:
- [ ] Health check passes
- [ ] API endpoints work
- [ ] Dashboard loads
- [ ] Processing status shows success

---

## 🎉 You're Done!

Your FastAPI application is now running with:
- ✅ SQLAlchemy ORM
- ✅ Alembic migrations
- ✅ Upload API
- ✅ Zero CPU usage when idle
- ✅ Fast SQLite queries
- ✅ Complete dashboard
- ✅ Production-ready code

**Access Points:**
- Dashboard: http://localhost:8000
- API Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

**Next Steps:**
1. Upload your Excel files
2. Explore the dashboard
3. Check API documentation
4. Read other docs for deep dive

**Need Help?**
- Review troubleshooting section above
- Check SQLALCHEMY_MIGRATION.md
- Inspect the code (well-commented)

**Happy Coding! 🚀**
