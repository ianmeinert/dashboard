# scripts/update-dashboard.sh - Update script that pulls code and restarts services
#!/bin/bash

LOG_FILE="/var/log/dashboard/update.log"
REPO_DIR="/opt/dashboard"

echo "$(date): Starting dashboard update..." >> $LOG_FILE

cd $REPO_DIR

# Check if there are any updates
git fetch origin
if git diff HEAD origin/main --quiet; then
    echo "$(date): No updates available" >> $LOG_FILE
    exit 0
fi

echo "$(date): Updates found, pulling changes..." >> $LOG_FILE
git pull origin main >> $LOG_FILE 2>&1

# Install any new Python dependencies
if [ -f "backend/requirements.txt" ]; then
    echo "$(date): Installing Python dependencies..." >> $LOG_FILE
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "$(date): Creating virtual environment..." >> $LOG_FILE
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install -r backend/requirements.txt >> $LOG_FILE 2>&1
fi

# Install any new Node.js dependencies
cd frontend
echo "$(date): Installing Node.js dependencies..." >> $LOG_FILE
npm install >> $LOG_FILE 2>&1
cd ..

# Restart services
echo "$(date): Restarting services..." >> $LOG_FILE
sudo systemctl restart dashboard-backend.service
sudo systemctl restart dashboard-frontend.service

echo "$(date): Update completed successfully" >> $LOG_FILE