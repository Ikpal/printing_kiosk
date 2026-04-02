from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from ..config import ADMIN_PASSWORD
from ..database import get_db_connection

router = APIRouter()
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, "admin")
    is_correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})
    return credentials.username

@router.get("/dashboard")
async def get_dashboard(username: str = Depends(verify_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total_jobs, SUM(amount_inr) as revenue FROM jobs WHERE payment_status = 'success'")
    stats = cursor.fetchone()
    
    conn.close()
    return {
        "total_jobs": stats['total_jobs'] or 0,
        "revenue": stats['revenue'] or 0,
        "printer_status": "online"
    }

@router.get("/jobs")
async def get_jobs(username: str = Depends(verify_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 100")
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs

@router.get("/pricing")
async def get_pricing(username: str = Depends(verify_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pricing")
    pricing = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return pricing

@router.post("/reprint/{job_id}")
async def reprint_job(job_id: str, username: str = Depends(verify_admin)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET print_status = 'waiting' WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    return {"message": "Job queued for reprint"}
