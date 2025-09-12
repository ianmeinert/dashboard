# scripts/start-backend.sh - Start the FastAPI backend
#!/bin/bash

cd /opt/dashboard
exec uvicorn backend.main:app --reload --host localhost --port 8000
