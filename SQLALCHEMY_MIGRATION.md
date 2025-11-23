# 🔄 SQLAlchemy Migration Guide

## Overview

The application has been upgraded from **raw SQLite3** to **SQLAlchemy ORM** with **Alembic migrations**.

---

## 🎯 Why SQLAlchemy?

### Benefits:
- ✅ **ORM (Object-Relational Mapping)** - Work with Python objects instead of SQL
- ✅ **Type Safety** - Better IDE support and type checking
- ✅ **Migrations** - Track database schema changes with Alembic
- ✅ **Better Performance** - Bulk operations, connection pooling
- ✅ **Relationships** - Easy to define and query related data
- ✅ **Database Agnostic** - Easy to switch from SQLite to PostgreSQL later
- ✅ **Professional Standard** - Industry-standard ORM

---

## 📂 New File Structure

```
fastapi_architecture/
├── app/
│   ├── models/
│   │   ├── base.py                    # 🆕 SQLAlchemy Base Model
│   │   ├── stock_models.py            # 🆕 Stock ORM Models
│   │   └── schemas.py                 # (existing Pydantic schemas)
│   │
│   ├── core/
│   │   ├── database.py                # ❌ Deprecated (raw SQLite)
│   │   ├── database_sqlalchemy.py     # 🆕 SQLAlchemy Database Manager
│   │   └── config.py
│   │
│   └── services/
│       ├── data_processor.py          # ✏️ Updated to use SQLAlchemy
│       ├── stock_service.py           # ✏️ Updated to use SQLAlchemy
│       └── excel_utils.py
│
├── alembic/                           # 🆕 Migration system
│   ├── versions/
│   │   └── 001_initial_migration.py   # Initial schema
│   ├── env.py                         # Alembic environment
│   └── script.py.mako                 # Migration template
│
├── alembic.ini                        # 🆕 Alembic configuration
└── requirements.txt                   # ✏️ Added SQLAlchemy + Alembic
```

---

## 🗂️ SQLAlchemy Models

### Base Model (`app/models/base.py`)

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

### Stock Models (`app/models/stock_models.py`)

**4 Models:**
1. **HistoricalData** - Historical stock data
2. **LiveData** - Live stock data
3. **ProcessingMetadata** - Processing logs
4. **UploadedFile** - File upload tracking

**Example:**
```python
class HistoricalData(BaseModel):
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
    
    def to_dict(self):
        return {
            "Stock": self.stock,
            "Category": self.category or "",
            # ... more fields
        }
```

---

## 🔧 Database Manager (`database_sqlalchemy.py`)

### Key Features:

**Session Management:**
```python
# Context manager for transactions
with db.get_session() as session:
    session.add(object)
    # auto-commits on exit

# Dependency injection for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Bulk Operations (Fast!):**
```python
# Insert multiple records efficiently
db.bulk_insert_historical(stock, data_list)
db.bulk_insert_live(stock, data_list)
```

**Query Methods:**
```python
# Get data
historical = db.get_historical_data("RELIANCE")
live = db.get_live_data("RELIANCE")

# Get all stocks
stocks = db.get_all_stocks_from_db()

# Clear data
db.clear_stock_data()  # All stocks
db.clear_stock_data("RELIANCE")  # Single stock

# Logging
db.log_processing("full_process", 218, "success", "Completed")
db.log_file_upload("Historical", "Historical.xlsx", 245760)
```

---

## 🔄 Alembic Migrations

### What are Migrations?

Migrations track database schema changes over time. Like Git for your database!

### Commands:

**Initialize (already done):**
```bash
alembic init alembic
```

**Run existing migration:**
```bash
alembic upgrade head
```

**Check current version:**
```bash
alembic current
```

**View migration history:**
```bash
alembic history
```

**Create new migration (auto-generate):**
```bash
alembic revision --autogenerate -m "Add new column"
```

**Rollback migration:**
```bash
alembic downgrade -1
```

---

## 📦 Installation & Setup

### Step 1: Install Dependencies

```bash
cd /media/rokkun09/271fcf58-e03d-46d8-a9cd-3425ed858c65/kk/fastapi_architecture
pip install -r requirements.txt
```

This installs:
- `sqlalchemy==2.0.25`
- `alembic==1.13.1`

### Step 2: Run Migrations

```bash
# Apply database schema
alembic upgrade head
```

Output:
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration - Create stock data tables
```

### Step 3: Verify Database

```bash
sqlite3 options_data.db ".tables"
```

Should show:
```
alembic_version      live_data            uploaded_files     
historical_data      processing_metadata
```

---

## 🔄 Migration from Old System

### Old System (Raw SQLite):
```python
# app/core/database.py
conn = sqlite3.connect("options_data.db")
cursor = conn.cursor()
cursor.execute("INSERT INTO historical_data ...")
conn.commit()
```

### New System (SQLAlchemy):
```python
# app/core/database_sqlalchemy.py
with db.get_session() as session:
    historical = HistoricalData(
        stock="RELIANCE",
        category="Call Resistance",
        strike="3000"
    )
    session.add(historical)
# auto-commits
```

### Benefits:
- ✅ No manual SQL strings
- ✅ Type-safe
- ✅ Auto-commit/rollback
- ✅ Connection pooling
- ✅ Bulk operations

---

## 🚀 Usage Examples

### Insert Single Record:
```python
from app.core.database_sqlalchemy import db

db.insert_historical_data("RELIANCE", {
    "Category": "Call Resistance",
    "Strike": "3000",
    "Prev_OI": "10000",
    "Latest_OI": "12000",
    "LTP": "2950.50"
})
```

### Bulk Insert (Faster):
```python
data_list = [
    {"Category": "Call Resistance", "Strike": "3000", ...},
    {"Category": "Put Support", "Strike": "2900", ...},
]

db.bulk_insert_historical("RELIANCE", data_list)
```

### Query Data:
```python
# Get all historical data for a stock
historical = db.get_historical_data("RELIANCE")
# Returns: List[Dict]

# Get all stocks
stocks = db.get_all_stocks_from_db()
# Returns: ['ABB', 'RELIANCE', 'TCS', ...]
```

### Direct ORM Query (Advanced):
```python
from app.models.stock_models import HistoricalData

with db.get_session() as session:
    # Query with filters
    results = session.query(HistoricalData).filter(
        HistoricalData.stock == "RELIANCE",
        HistoricalData.strike == "3000"
    ).all()
    
    # Count records
    count = session.query(HistoricalData).filter(
        HistoricalData.stock == "RELIANCE"
    ).count()
```

---

## 🔍 Comparison

| Feature | Raw SQLite | SQLAlchemy |
|---------|-----------|------------|
| **Code Style** | SQL strings | Python objects |
| **Type Safety** | ❌ None | ✅ Full |
| **Migrations** | ❌ Manual | ✅ Alembic |
| **Relationships** | ❌ Manual joins | ✅ Automatic |
| **Bulk Operations** | ⚠️ Manual | ✅ Built-in |
| **Database Switch** | ❌ Hard | ✅ Easy |
| **IDE Support** | ⚠️ Limited | ✅ Excellent |
| **Performance** | ⚠️ Manual optimization | ✅ Built-in pooling |

---

## 📝 Creating New Migrations

### Scenario: Add a new column

**Step 1: Update Model**

Edit `app/models/stock_models.py`:
```python
class HistoricalData(BaseModel):
    # ... existing fields ...
    volume = Column(Integer)  # New field
```

**Step 2: Generate Migration**
```bash
alembic revision --autogenerate -m "Add volume column to historical_data"
```

**Step 3: Review Migration**

Check `alembic/versions/002_add_volume_column.py`:
```python
def upgrade():
    op.add_column('historical_data', sa.Column('volume', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('historical_data', 'volume')
```

**Step 4: Apply Migration**
```bash
alembic upgrade head
```

---

## 🛠️ Troubleshooting

### Issue: "No module named 'sqlalchemy'"
**Solution:**
```bash
pip install sqlalchemy==2.0.25 alembic==1.13.1
```

### Issue: "Table already exists"
**Solution:**
```bash
# Delete old database
rm options_data.db

# Run migrations fresh
alembic upgrade head
```

### Issue: Migration out of sync
**Solution:**
```bash
# Check current version
alembic current

# Reset to base
alembic downgrade base

# Reapply all
alembic upgrade head
```

### Issue: Need to rollback
**Solution:**
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade 001
```

---

## 📚 Database Schema

### Tables Created:

**1. historical_data**
- Columns: id, created_at, updated_at, stock, category, strike, prev_oi, latest_oi, call_oi_difference, put_oi_difference, ltp, additional_strike
- Index: stock

**2. live_data**
- Columns: id, created_at, updated_at, stock, section, label, prev_oi, strike, oi_diff, is_new_strike, add_strike
- Index: stock

**3. processing_metadata**
- Columns: id, created_at, updated_at, process_type, stocks_processed, status, message, processed_at

**4. uploaded_files**
- Columns: id, created_at, updated_at, file_type, file_name, file_size, uploaded_at

**5. alembic_version** (Alembic tracking)
- Columns: version_num

---

## 🎯 Next Steps

### After Migration:

1. **Start server:**
```bash
python main.py
```

2. **Upload files:**
```bash
python test_upload.py Historical.xlsx Live.xlsx
```

3. **Verify data:**
```bash
sqlite3 options_data.db "SELECT COUNT(*) FROM historical_data;"
```

4. **Access dashboard:**
```
http://localhost:8000
```

---

## 🚀 Performance Improvements

### Bulk Insert Performance:

**Old (Individual Inserts):**
```python
for data in data_list:  # 220 stocks × ~10 rows each
    db.insert_historical_data(stock, data)
# 2,200 individual transactions = SLOW
```

**New (Bulk Insert):**
```python
db.bulk_insert_historical(stock, data_list)
# Single transaction = FAST (10-50x faster)
```

### Expected Processing Time:
- **Old:** 30-45 seconds for 220 stocks
- **New:** 10-20 seconds for 220 stocks

---

## 🎓 Learning Resources

### SQLAlchemy:
- Official Docs: https://docs.sqlalchemy.org/
- Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/

### Alembic:
- Official Docs: https://alembic.sqlalchemy.org/
- Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html

### Examples:
- Query: https://docs.sqlalchemy.org/en/20/orm/queryguide/
- Relationships: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html

---

## ✅ Migration Checklist

- [x] Created SQLAlchemy Base Model
- [x] Created Stock ORM Models (4 tables)
- [x] Created SQLAlchemy Database Manager
- [x] Updated Data Processor to use SQLAlchemy
- [x] Updated Stock Service to use SQLAlchemy
- [x] Updated Upload API to use SQLAlchemy
- [x] Set up Alembic migrations
- [x] Created initial migration (001)
- [x] Updated requirements.txt
- [x] Added bulk insert optimization
- [x] Added proper indexing

---

## 🎉 Summary

**You now have:**
- ✅ Professional SQLAlchemy ORM
- ✅ Alembic migration system
- ✅ Type-safe database models
- ✅ Bulk insert optimization
- ✅ Better IDE support
- ✅ Migration tracking
- ✅ Production-ready code

**Everything still works the same from the user perspective, but now with much better code quality!**
