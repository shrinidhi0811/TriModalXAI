#!/bin/sh
# Startup script for Railway deployment

echo "Starting TriModal XAI Backend..."
echo "PORT environment variable: ${PORT}"

# Use PORT if set by Railway, otherwise default to 8000
ACTUAL_PORT=${PORT:-8000}

echo "Starting uvicorn on port: $ACTUAL_PORT"

exec uvicorn app:app --host 0.0.0.0 --port $ACTUAL_PORT --workers 1
