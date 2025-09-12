# scripts/start-kiosk.sh - Start Chromium in kiosk mode
#!/bin/bash

# Wait for services to be ready
sleep 10

# Start Chromium in kiosk mode
exec chromium-browser \
    --kiosk \
    --no-first-run \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-translate \
    --disable-features=VizDisplayCompositor \
    --start-fullscreen \
    --app=http://localhost:5173
