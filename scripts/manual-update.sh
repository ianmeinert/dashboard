#!/bin/bash
# scripts/manual-update.sh - Manual update script for user login trigger

echo "Checking for updates..."
/usr/local/bin/update-dashboard.sh

echo "Update check complete. Services restarted if needed."