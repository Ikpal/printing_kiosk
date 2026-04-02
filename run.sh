#!/bin/bash

# Ensure db and tmp directories exist
mkdir -p db
mkdir -p tmp/kiosk_jobs

# Start the FastAPI backend in the background
echo "Starting backend server..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start the background print worker
echo "Starting print manager worker..."
python print_manager/worker.py &
WORKER_PID=$!

# Trap termination signals to kill both processes
trap "kill $BACKEND_PID $WORKER_PID" EXIT

# Wait for both background processes
wait
