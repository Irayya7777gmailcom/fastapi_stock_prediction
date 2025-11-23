#!/bin/bash
# FastAPI Application Launcher

echo "🚀 Starting Options Dashboard FastAPI Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Run the application
echo "✅ Starting server on http://0.0.0.0:8000"
python main.py
