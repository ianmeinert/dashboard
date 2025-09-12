# scripts/start-backend.sh - Start the FastAPI backend
#!/bin/bash

cd /opt/dashboard

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found, creating..."
    python3 -m venv venv
    venv/bin/pip install -r backend/requirements.txt
fi

# Use absolute path to venv python and uvicorn
exec /opt/dashboard/venv/bin/uvicorn backend.main:app --reload --host localhost --port 8000