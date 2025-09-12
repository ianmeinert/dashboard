# scripts/setup-login-update.sh - Setup script to trigger updates on user login
#!/bin/bash

# Create a script that runs on user login
cat > ~/.bashrc_dashboard << 'EOF'
# Dashboard update on login
if [ -f "/tmp/dashboard_login_update_done" ]; then
    # Already updated this session
    exit 0
fi

echo "Checking for dashboard updates..."
/usr/local/bin/update-dashboard.sh

# Mark as done for this session
touch /tmp/dashboard_login_update_done

# Clean up marker on logout
trap 'rm -f /tmp/dashboard_login_update_done' EXIT
EOF

# Add to .bashrc if not already there
if ! grep -q "source ~/.bashrc_dashboard" ~/.bashrc; then
    echo "source ~/.bashrc_dashboard" >> ~/.bashrc
fi

echo "Login update trigger configured"
