# Alternative: GUI-based update trigger for desktop login
# scripts/setup-gui-login-update.sh
#!/bin/bash

# Create desktop file for login update
cat > ~/.config/autostart/dashboard-update.desktop << EOF
[Desktop Entry]
Type=Application
Name=Dashboard Update
Exec=/opt/dashboard/scripts/manual-update.sh
Hidden=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

echo "GUI login update trigger configured"