# FastAPI Architecture Documentation

## 🏛️ Architecture Principles

### 1. **Separation of Concerns**
Each layer has a specific responsibility:
- **API Layer**: HTTP handling, routing, validation
- **Service Layer**: Business logic, data processing
- **Models Layer**: Data structures, validation schemas
- **Core Layer**: Configuration, utilities

### 2. **Dependency Inversion**
High-level modules don't depend on low-level modules. Both depend on abstractions.

### 3. **Single Responsibility**
Each module/class has one reason to change.

### 4. **DRY (Don't Repeat Yourself)**
Common functionality is extracted into utilities and services.

## 📂 Detailed Structure

### **main.py** - Application Entry Point
```python
# Responsibilities:
- FastAPI app initialization
- Middleware configuration
- Router registration
- Lifespan events (startup/shutdown)
- Static file mounting
```

### **app/core/config.py** - Configuration Management
```python
# Features:
- Pydantic Settings for type-safe config
- Environment variable loading
- Default values
- Validation
- Global settings instance
```

### **app/models/schemas.py** - Data Models
```python
# Contains:
- Request schemas
- Response schemas
- Data validation rules
- Type definitions
- Documentation strings
```

### **app/api/v1/** - API Routes
```
router.py           # Aggregates all endpoint routers
endpoints/
  ├── stocks.py     # Stock-related endpoints
  └── data_processing.py  # Processing endpoints
```

**Endpoint Design Pattern:**
```python
@router.get("/path", response_model=Schema)
async def endpoint_name(params) -> Schema:
    # 1. Validate input (automatic via Pydantic)
    # 2. Call service layer
    # 3. Handle errors
    # 4. Return response
```

### **app/services/** - Business Logic

#### **stock_service.py**
```python
# Responsibilities:
- Read JSON files
- Parse stock data
- Handle favorites
- Data transformation
```

#### **data_processor.py**
```python
# Responsibilities:
- Orchestrate data processing
- Manage processing state
- Atomic file writes
- Error handling
```

#### **excel_utils.py**
```python
# Responsibilities:
- Excel file reading
- Data extraction
- Date parsing
- Number formatting
- Strike key generation
```

## 🔄 Request Flow

```
1. Client Request
   ↓
2. FastAPI Router (main.py)
   ↓
3. Endpoint Handler (app/api/v1/endpoints/)
   ├── Pydantic validates request
   ↓
4. Service Layer (app/services/)
   ├── Business logic execution
   ├── Data access
   ↓
5. Response
   ├── Pydantic validates response
   ├── Automatic serialization
   ↓
6. Client receives JSON
```

## 🎯 Design Patterns Used

### 1. **Service Pattern**
```python
class StockService:
    async def get_all_stocks(self) -> List[str]:
        # Business logic here
```
**Benefits**: Testable, reusable, maintainable

### 2. **Repository Pattern** (Implicit)
```python
# Services act as repositories
stock_service.get_stock_summary(stock)
```
**Benefits**: Abstraction over data access

### 3. **Factory Pattern**
```python
settings = Settings()  # Factory for configuration
```

### 4. **Singleton Pattern**
```python
# Global settings instance
settings = Settings()
```

### 5. **Strategy Pattern**
```python
# Different processing strategies can be plugged in
class DataProcessorService:
    def process_all_stocks(self):
        # Strategy implementation
```

## 🔐 Error Handling Strategy

### Levels of Error Handling:

1. **Pydantic Validation** (Automatic)
   - Invalid input → 422 Unprocessable Entity

2. **Service Layer** (Try-Except)
   - Business logic errors
   - Data access errors

3. **Endpoint Layer** (HTTPException)
   - 404 Not Found
   - 500 Internal Server Error
   - Custom error messages

### Example:
```python
try:
    data = await service.get_data()
except FileNotFoundError:
    raise HTTPException(status_code=404, detail="Not found")
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

## 🚀 Performance Optimizations

### 1. **Async/Await**
```python
async def get_stock_summary(stock: str):
    # Non-blocking I/O operations
```

### 2. **Background Tasks**
```python
background_tasks.add_task(process_data)
# Returns immediately, processes in background
```

### 3. **Atomic File Writes**
```python
# Prevents partial reads during writes
atomic_write_json(path, data)
```

### 4. **Efficient Excel Reading**
```python
# Read into memory to avoid file locks
with open(path, "rb") as f:
    pd.read_excel(BytesIO(f.read()))
```

## 📊 Data Processing Architecture

```
Excel Files (live_data/)
    ↓
ExcelUtils.extract_historical_table()
ExcelUtils.extract_live_table()
    ↓
DataProcessorService.process_all_stocks()
    ↓
Atomic JSON writes (processed/)
    ↓
StockService reads JSON
    ↓
API returns data
```

## 🔧 Configuration Hierarchy

```
1. Default values (config.py)
   ↓
2. .env file
   ↓
3. Environment variables
   ↓
4. Runtime overrides
```

## 🧪 Testing Strategy

### Unit Tests
```python
# Test individual functions
def test_format_number():
    assert format_number(1000) == "1,000"
```

### Integration Tests
```python
# Test service interactions
async def test_get_stock_summary():
    service = StockService()
    result = await service.get_stock_summary("RELIANCE")
    assert result.historical is not None
```

### API Tests
```python
# Test endpoints
async def test_stocks_endpoint():
    response = client.get("/api/v1/stocks/")
    assert response.status_code == 200
```

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless design
- No in-memory session storage
- File-based data (can be moved to DB)

### Vertical Scaling
- Async operations
- Background tasks
- Efficient data processing

### Future Enhancements
1. **Database Integration**
   - Replace JSON files with PostgreSQL/MongoDB
   - Add SQLAlchemy/Motor

2. **Caching**
   - Redis for frequently accessed data
   - In-memory caching with TTL

3. **Message Queue**
   - RabbitMQ/Celery for heavy processing
   - Distributed task processing

4. **WebSockets**
   - Real-time data updates
   - Live notifications

## 🔒 Security Best Practices

1. **Input Validation**: Pydantic schemas
2. **Path Sanitization**: Prevent directory traversal
3. **CORS Configuration**: Restrict origins in production
4. **Environment Variables**: No hardcoded secrets
5. **Rate Limiting**: Add middleware for API limits
6. **Authentication**: JWT tokens (future enhancement)

## 📚 API Versioning Strategy

```
/api/v1/  ← Current version
/api/v2/  ← Future version

# Allows backward compatibility
```

## 🎨 Code Style Guidelines

1. **Type Hints**: Always use type annotations
2. **Docstrings**: Document all public functions
3. **Naming**: 
   - Classes: PascalCase
   - Functions: snake_case
   - Constants: UPPER_CASE
4. **Line Length**: Max 100 characters
5. **Imports**: Organized (stdlib, third-party, local)

## 🔄 Deployment Architecture

```
[Nginx] → [Uvicorn Workers] → [FastAPI App]
   ↓
[Static Files]
   ↓
[Data Files]
```

### Recommended Setup:
- **Nginx**: Reverse proxy, SSL, static files
- **Uvicorn**: ASGI server with multiple workers
- **Supervisor/Systemd**: Process management
- **Docker**: Containerization

## 📊 Monitoring & Logging

### Logging Strategy:
```python
import logging

logger = logging.getLogger(__name__)
logger.info("Processing started")
logger.error("Error occurred", exc_info=True)
```

### Metrics to Track:
- Request count
- Response time
- Error rate
- Data processing time
- Active connections

## 🎯 Migration Path from Flask

1. ✅ **Phase 1**: Create FastAPI structure (Done)
2. ⏳ **Phase 2**: Run both Flask & FastAPI in parallel
3. ⏳ **Phase 3**: Migrate frontend to use FastAPI endpoints
4. ⏳ **Phase 4**: Deprecate Flask endpoints
5. ⏳ **Phase 5**: Remove Flask completely

---

**This architecture is designed for:**
- ✅ Maintainability
- ✅ Scalability
- ✅ Testability
- ✅ Performance
- ✅ Developer Experience
