from fastapi import APIRouter, UploadFile, File, Request, HTTPException
import uuid
import os
from datetime import datetime
from ..config import MAX_FILE_SIZE_MB, ALLOWED_MIME_TYPES
from ..database import get_db_connection

router = APIRouter()

upload_history = {}

def check_rate_limit(client_ip: str):
    now = datetime.now()
    if client_ip in upload_history:
        times = upload_history[client_ip]
        times = [t for t in times if (now - t).total_seconds() < 60]
        if len(times) >= 5:
            return False
        times.append(now)
        upload_history[client_ip] = times
    else:
        upload_history[client_ip] = [now]
    return True

import socket

upload_sessions = {}

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

@router.get("/session/new")
async def create_session():
    session_id = str(uuid.uuid4())
    upload_sessions[session_id] = None
    lan_ip = get_lan_ip()
    url = f"http://{lan_ip}:8000/mobile/{session_id}"
    return {"session_id": session_id, "url": url}

@router.get("/session/{session_id}")
async def check_session(session_id: str):
    if session_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Invalid session")
    job_id = upload_sessions[session_id]
    return {"job_id": job_id}

async def handle_upload_logic(request: Request, file: UploadFile):
    client_ip = request.client.host
    if not check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 5 uploads per minute.")

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, DOCX, JPG, PNG allowed.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed.")

    job_id = str(uuid.uuid4())
    extension = ALLOWED_MIME_TYPES[file.content_type]
    safe_filename = f"{job_id}{extension}"
    
    job_dir = os.path.join("tmp", "kiosk_jobs", job_id)
    os.makedirs(job_dir, exist_ok=True)
    file_path = os.path.join(job_dir, safe_filename)

    with open(file_path, "wb") as f:
        f.write(contents)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO jobs (job_id, filename, file_path)
        VALUES (?, ?, ?)
    """, (job_id, file.filename, file_path))
    conn.commit()
    conn.close()
    
    return job_id

@router.post("")
async def upload_file(request: Request, file: UploadFile = File(...)):
    job_id = await handle_upload_logic(request, file)
    return {"job_id": job_id, "message": "File uploaded successfully"}
