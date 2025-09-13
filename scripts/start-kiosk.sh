# scripts/start-kiosk.sh - Start Chromium in kiosk mode
#!/bin/bash

# Wait for services to be ready
sleep 10

# Start Firefox in kiosk mode
exec firefox \
    --kiosk \
      http://localhost:5173