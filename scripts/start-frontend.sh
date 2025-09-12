# scripts/start-frontend.sh - Start the Node.js frontend
#!/bin/bash

cd /opt/dashboard/frontend
exec npm run dev -- --host localhost --port 5173