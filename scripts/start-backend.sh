# First, delete the problematic script
rm /opt/dashboard/scripts/start-backend.sh

# Create a new one with a simple echo approach
echo '#!/bin/bash

cd /opt/dashboard

# Ensure virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found, creating..."
    python3 -m venv venv
    venv/bin/pip install -r backend/requirements.txt
fi

# Use absolute path to venv python and uvicorn
exec /opt/dashboard/venv/bin/uvicorn backend.main:app --reload --host localhost --port 8000' > /opt/dashboard/scripts/start-backend.sh

# Make it executable
chmod +x /opt/dashboard/scripts/start-backend.sh

# Check the file format
file /opt/dashboard/scripts/start-backend.sh

# Test it manually
/opt/dashboard/scripts/start-backend.sh