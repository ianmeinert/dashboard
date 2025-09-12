#!/bin/bash
# kiosk-setup.sh - Initial setup script for the kiosk system

set -e

echo "Setting up kiosk system..."

# Get the current directory (should be the project root)
PROJECT_DIR=$(pwd)

# Verify we're in a git repository
if [ ! -d ".git" ]; then
    echo "Error: This script must be run from the root of the dashboard git repository"
    exit 1
fi

echo "Current project directory: $PROJECT_DIR"

# Create directories
sudo mkdir -p /opt/dashboard
sudo mkdir -p /var/log/dashboard
sudo chown $USER:$USER /opt/dashboard /var/log/dashboard

# Copy/move the current project to /opt/dashboard if it's not already there
if [ "$PROJECT_DIR" != "/opt/dashboard" ]; then
    echo "Copying project to /opt/dashboard..."
    sudo cp -r . /opt/dashboard/
    sudo chown -R $USER:$USER /opt/dashboard
    
    # Update the working directory
    cd /opt/dashboard
    
    # Ensure git remote is set correctly
    git remote set-url origin https://github.com/ianmeinert/dashboard.git
else
    echo "Already in /opt/dashboard, pulling latest changes..."
    git pull
fi

# Create Python virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists, skipping creation..."
fi

source venv/bin/activate

# Install Python dependencies (assuming requirements.txt exists)
if [ -f "backend/requirements.txt" ]; then
    pip3 install -r backend/requirements.txt
fi

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Make scripts executable
chmod +x /opt/dashboard/scripts/*.sh

# Copy systemd service files
sudo cp scripts/dashboard-backend.service /etc/systemd/system/
sudo cp scripts/dashboard-frontend.service /etc/systemd/system/
sudo cp scripts/dashboard-update.service /etc/systemd/system/
sudo cp scripts/dashboard-update.timer /etc/systemd/system/

# Create the update script
sudo cp scripts/update-dashboard.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/update-dashboard.sh

# Reload systemd and enable services
sudo systemctl daemon-reload
sudo systemctl enable dashboard-backend.service
sudo systemctl enable dashboard-frontend.service
sudo systemctl enable dashboard-update.timer

# Start services
sudo systemctl start dashboard-backend.service
sudo systemctl start dashboard-frontend.service
sudo systemctl start dashboard-update.timer

echo "Kiosk setup complete!"
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:5173"
echo "Services will auto-update via timer"

# Setup chromium kiosk mode
echo "Setting up Chromium kiosk mode..."
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/kiosk.desktop << EOF
[Desktop Entry]
Type=Application
Name=Kiosk Mode
Exec=/opt/dashboard/scripts/start-kiosk.sh
Hidden=false
X-GNOME-Autostart-enabled=true
EOF

echo "Chromium will start in kiosk mode on login"
echo "Reboot to test the complete setup"