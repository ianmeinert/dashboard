# scripts/start-kiosk.sh - Start Chromium in kiosk mode
#!/bin/bash

# Wait for services to be ready
sleep 10

# Start Chromium in kiosk mode
exec chromium-browser \
    --app=http://localhost:5173 \
    --start-fullscreen \
    --no-first-run \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-web-security \
    --enable-features=OverlayScrollbar