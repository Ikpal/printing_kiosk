@echo off
echo Creating directories...
if not exist db mkdir db
if not exist tmp\kiosk_jobs mkdir tmp\kiosk_jobs

echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k ".\venv\Scripts\uvicorn.exe backend.main:app --host 0.0.0.0 --port 8000"

echo Starting Print Worker...
start "Print Worker" cmd /k ".\venv\Scripts\python.exe print_manager\worker.py"

echo Both services have been started in new windows.
