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

# Install Python dependencies from backend directory
if [ -f "backend/requirements.txt" ]; then
    echo "Installing Python dependencies from backend/requirements.txt..."
    pip install -r backend/requirements.txt
fi

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Fix line endings and create scripts with proper Unix format
echo "Creating script files with proper Unix line endings..."

# Create start-backend.sh
cat > scripts/start-backend.sh << 'EOF'
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
EOF

# Create start-frontend.sh
cat > scripts/start-frontend.sh << 'EOF'
#!/bin/bash

cd /opt/dashboard/frontend
exec npm run dev -- --host localhost --port 5173
EOF

# Create start-kiosk.sh
cat > scripts/start-kiosk.sh << 'EOF'
#!/bin/bash

# Wait for services to be ready
sleep 10

# Start Chromium in kiosk mode
exec chromium-browser \
    --kiosk \
      http://localhost:5173 \
    --no-first-run \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-web-security \
    --enable-features=OverlayScrollbar
EOF

# Create manual-update.sh
cat > scripts/manual-update.sh << 'EOF'
#!/bin/bash

echo "Checking for updates..."
/usr/local/bin/update-dashboard.sh

echo "Update check complete. Services restarted if needed."
EOF

# Create systemd service files with current user
echo "Creating systemd service files..."

# Create backend service file
cat > scripts/dashboard-backend.service << EOF
[Unit]
Description=Dashboard Backend Service
After=network.target
Wants=network-online.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=/opt/dashboard
ExecStart=/opt/dashboard/scripts/start-backend.sh
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
Environment=PYTHONPATH=/opt/dashboard

[Install]
WantedBy=multi-user.target
EOF

# Create frontend service file
cat > scripts/dashboard-frontend.service << EOF
[Unit]
Description=Dashboard Frontend Service
After=network.target dashboard-backend.service
Wants=network-online.target
Requires=dashboard-backend.service

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=/opt/dashboard/frontend
ExecStart=/opt/dashboard/scripts/start-frontend.sh
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create update service file
cat > scripts/dashboard-update.service << EOF
[Unit]
Description=Dashboard Update Service
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=$USER
Group=$USER
ExecStart=/usr/local/bin/update-dashboard.sh
EOF

# Create update timer file
cat > scripts/dashboard-update.timer << EOF
[Unit]
Description=Dashboard Update Timer
Requires=dashboard-update.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=10min
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Make scripts executable
echo "Making scripts executable..."
chmod +x scripts/*.sh
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

# Ensure chromium is installed
if ! command -v chromium-browser &> /dev/null; then
    echo "Installing Chromium..."
    sudo apt install chromium-browser -y
fi

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