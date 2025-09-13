# scripts/start-kiosk.sh - Start Chromium in kiosk mode
#!/bin/bash

# Wait for services to be ready
sleep 10

# Enable on-screen keyboard first
export GTK_IM_MODULE=ibus
export QT_IM_MODULE=ibus

# Start Chromium in kiosk mode
exec chromium-browser \
    --kiosk \
    --enable-virtual-keyboard \
    --app=http://localhost:5173 \
    --no-first-run \
    --touch-events=enabled