# Options Dashboard - FastAPI Architecture

Modern FastAPI-based REST API for Live Options Open Interest (OI) Tracking.

## 📁 Project Structure

```
fastapi_architecture/
├── main.py                      # FastAPI application entry point
├── app/
│   ├── __init__.py
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py        # Main API router
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── stocks.py    # Stock data endpoints
│   │           └── data_processing.py  # Data refresh endpoints
│   ├── core/                    # Core configuration
│   │   ├── __init__.py
│   │   └── config.py            # Settings & configuration
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py           # Request/Response schemas
│   └── services/                # Business logic
│       ├── __init__.py
│       ├── stock_service.py     # Stock data operations
│       ├── data_processor.py    # Excel processing
│       └── excel_utils.py       # Excel helper functions
├── pyproject.toml               # Poetry dependencies
├── requirements.txt             # Pip dependencies
├── .env.example                 # Environment variables template
├── .gitignore
└── README.md
```

## 🏗️ Architecture Overview

### **Layered Architecture**

1. **API Layer** (`app/api/`)
   - RESTful endpoints
   - Request validation
   - Response formatting
   - Error handling

2. **Service Layer** (`app/services/`)
   - Business logic
   - Data processing
   - Excel file operations
   - JSON generation

3. **Models Layer** (`app/models/`)
   - Pydantic schemas
   - Data validation
   - Type safety

4. **Core Layer** (`app/core/`)
   - Configuration management
   - Settings
   - Constants

## 🚀 Features

- ✅ **RESTful API** with FastAPI
- ✅ **Automatic API Documentation** (Swagger UI & ReDoc)
- ✅ **Pydantic Validation** for type safety
- ✅ **Async/Await** support
- ✅ **CORS** enabled
- ✅ **Environment-based Configuration**
- ✅ **Static File Serving**
- ✅ **Background Tasks** for data processing
- ✅ **Health Check** endpoint
- ✅ **Modular & Scalable** structure

## 📦 Dependencies

### Core Dependencies
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Pandas** - Data processing
- **OpenPyXL** - Excel file handling
- **Python-dotenv** - Environment management

### Development Dependencies
- **Pytest** - Testing framework
- **Black** - Code formatting
- **Flake8** - Linting
- **MyPy** - Type checking

## 🔧 Installation

### Option 1: Using pip
```bash
cd fastapi_architecture
pip install -r requirements.txt
```

### Option 2: Using Poetry
```bash
cd fastapi_architecture
poetry install
```

## ⚙️ Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Update environment variables:
```env
LIVE_DATA_DIR=../live_data
PROCESSED_DIR=../processed
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🏃 Running the Application

### Development Mode
```bash
# Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 API Endpoints

### Stock Endpoints

#### Get All Stocks
```http
GET /api/v1/stocks/
```
Returns list of all available stock symbols.

#### Get Stock Summary
```http
GET /api/v1/stocks/{stock}
```
Returns historical and live data for a specific stock.

**Example:**
```bash
curl http://localhost:8000/api/v1/stocks/RELIANCE
```

#### Get Favorite Stocks
```http
GET /api/v1/stocks/favorites/list
```
Returns list of favorite stocks from `favorites.txt`.

### Data Processing Endpoints

#### Trigger Data Refresh
```http
POST /api/v1/process/refresh
```
Manually trigger data processing (runs in background).

#### Get Processing Status
```http
GET /api/v1/process/status
```
Get current status of data processing.

### Utility Endpoints

#### Health Check
```http
GET /health
```
Returns application health status.

#### Root
```http
GET /
```
Serves the main HTML dashboard.

## 📖 API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## 🔄 Data Flow

1. **Excel Files** (Historical.xlsx, Live.xlsx) → Stored in `live_data/`
2. **Data Processor Service** → Reads Excel files
3. **JSON Generation** → Atomic writes to `processed/`
4. **Stock Service** → Reads JSON files
5. **API Endpoints** → Returns data to clients

## 🎯 Key Design Patterns

### 1. **Dependency Injection**
Services are instantiated and injected where needed.

### 2. **Repository Pattern**
Data access is abstracted through service layer.

### 3. **DTO Pattern**
Pydantic schemas act as Data Transfer Objects.

### 4. **Separation of Concerns**
Clear separation between API, business logic, and data access.

### 5. **Configuration Management**
Centralized settings using Pydantic Settings.

## 🔐 Security Considerations

- CORS configured (update `ALLOWED_ORIGINS` for production)
- Environment variables for sensitive data
- Input validation via Pydantic
- Path traversal protection

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

## 📊 Comparison: Flask vs FastAPI

| Feature | Flask (Original) | FastAPI (New) |
|---------|-----------------|---------------|
| Framework | Flask | FastAPI |
| Async Support | ❌ | ✅ |
| Auto Documentation | ❌ | ✅ |
| Type Safety | ❌ | ✅ (Pydantic) |
| Performance | Good | Excellent |
| Validation | Manual | Automatic |
| API Standards | Custom | OpenAPI |

## 🚀 Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Systemd Service
```ini
[Unit]
Description=Options Dashboard API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/fastapi_architecture
ExecStart=/usr/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📝 Migration from Flask

The FastAPI architecture maintains compatibility with existing:
- ✅ Static files (`static/`)
- ✅ HTML templates (`templates/`)
- ✅ Data processing logic (`run_live.py`)
- ✅ Excel file formats
- ✅ JSON output structure

## 🤝 Contributing

1. Follow PEP 8 style guide
2. Use type hints
3. Write docstrings
4. Add tests for new features
5. Update documentation

## 📄 License

[Your License Here]

## 👥 Authors

[Your Name/Team]

---

**Note**: This is a production-ready FastAPI architecture based on the existing Flask application. All business logic from `run_live.py` has been refactored into services for better maintainability and scalability.
