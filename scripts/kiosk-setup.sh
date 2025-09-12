#!/bin/bash
# kiosk-setup.sh - Initial setup script for the kiosk system

set -e

echo "Setting up kiosk system..."

# Create directories
sudo mkdir -p /opt/dashboard
sudo mkdir -p /var/log/dashboard
sudo chown $USER:$USER /opt/dashboard /var/log/dashboard

# Clone the repository
cd /opt
if [ -d "dashboard" ]; then
    echo "Dashboard directory exists, pulling latest changes..."
    cd dashboard
    git pull
else
    echo "Cloning dashboard repository..."
    git clone https://github.com/ianmeinert/dashboard.git
    cd dashboard
fi

# Install Python dependencies (assuming requirements.txt exists)
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
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