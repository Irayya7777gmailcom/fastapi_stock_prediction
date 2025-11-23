# 🚀 Quick Start Guide

Get the Options Dashboard FastAPI running in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- pip or poetry
- Git (optional)

## 📥 Installation

### Step 1: Navigate to Directory
```bash
cd options-dashboard/fastapi_architecture
```

### Step 2: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
cp .env.example .env
```

Edit `.env` if needed:
```env
LIVE_DATA_DIR=../live_data
PROCESSED_DIR=../processed
HOST=0.0.0.0
PORT=8000
```

### Step 5: Run the Application
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 Access the Application

Once running, open your browser:

- **Main Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Alternative Docs**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Test the API

### Using curl:
```bash
# Get all stocks
curl http://localhost:8000/api/v1/stocks/

# Get specific stock
curl http://localhost:8000/api/v1/stocks/RELIANCE

# Get favorites
curl http://localhost:8000/api/v1/stocks/favorites/list

# Trigger data refresh
curl -X POST http://localhost:8000/api/v1/process/refresh
```

### Using Python:
```python
import requests

# Get all stocks
response = requests.get("http://localhost:8000/api/v1/stocks/")
print(response.json())

# Get stock summary
response = requests.get("http://localhost:8000/api/v1/stocks/RELIANCE")
print(response.json())
```

### Using JavaScript:
```javascript
// Get all stocks
fetch('http://localhost:8000/api/v1/stocks/')
  .then(res => res.json())
  .then(data => console.log(data));

// Get stock summary
fetch('http://localhost:8000/api/v1/stocks/RELIANCE')
  .then(res => res.json())
  .then(data => console.log(data));
```

## 📁 Directory Structure

```
fastapi_architecture/
├── main.py              # Start here - main application
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Configuration
│   ├── models/         # Data models
│   └── services/       # Business logic
├── requirements.txt    # Dependencies
└── .env               # Configuration
```

## 🔧 Common Commands

```bash
# Start server
python main.py

# Start with auto-reload (development)
uvicorn main:app --reload

# Start with multiple workers (production)
uvicorn main:app --workers 4

# Run tests
pytest

# Format code
black .

# Check code style
flake8
```

## 🐳 Using Docker

```bash
# Build image
docker build -t options-api .

# Run container
docker run -p 8000:8000 options-api

# Or use docker-compose
docker-compose up
```

## 📊 API Endpoints Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main dashboard |
| GET | `/health` | Health check |
| GET | `/api/v1/stocks/` | Get all stocks |
| GET | `/api/v1/stocks/{stock}` | Get stock summary |
| GET | `/api/v1/stocks/favorites/list` | Get favorites |
| POST | `/api/v1/process/refresh` | Trigger data refresh |
| GET | `/api/v1/process/status` | Get processing status |

## 🎯 Next Steps

1. ✅ **Explore API Docs**: Visit http://localhost:8000/api/docs
2. ✅ **Test Endpoints**: Use the interactive Swagger UI
3. ✅ **Check Logs**: Monitor console output
4. ✅ **Customize Config**: Edit `.env` file
5. ✅ **Read Full Docs**: Check `README.md` and `ARCHITECTURE.md`

## ❓ Troubleshooting

### Port Already in Use
```bash
# Change port in .env or use:
uvicorn main:app --port 8001
```

### Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

### Data Not Loading
```bash
# Check directories exist
mkdir -p ../live_data ../processed

# Verify .env paths
cat .env
```

### Permission Denied
```bash
# Make run script executable
chmod +x run.sh
./run.sh
```

## 📚 Learn More

- **Full Documentation**: `README.md`
- **Architecture Details**: `ARCHITECTURE.md`
- **Deployment Guide**: `DEPLOYMENT.md`
- **Flask Comparison**: `COMPARISON.md`

## 🎉 Success!

You're now running the FastAPI Options Dashboard! 

Visit http://localhost:8000/api/docs to explore the API.

---

**Need help?** Check the documentation or review the logs for error messages.
