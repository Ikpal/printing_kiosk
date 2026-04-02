import os
import time
import sqlite3
import subprocess
import logging
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./db/kiosk.db").replace("sqlite:///", "")
MOCK_PRINTER = os.getenv("MOCK_PRINTER", "true").lower() == "true"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def process_job(job):
    job_id = job['job_id']
    file_path = job['file_path']
    copies = job['copies'] or 1
    color_mode = job['color_mode']
    duplex = job['duplex']
    
    logging.info(f"Processing job {job_id}: {copies} copies, {color_mode}, duplex={duplex}")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET print_status = 'printing' WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    
    cmd = ["lp", "-n", str(copies)]
    
    if duplex:
        cmd.extend(["-o", "sides=two-sided-long-edge"])
    else:
        cmd.extend(["-o", "sides=one-sided"])
        
    if color_mode == 'bw':
        cmd.extend(["-o", "ColorModel=Gray"])
    else:
        cmd.extend(["-o", "ColorModel=RGB"])
        
    cmd.append(file_path)
    
    try:
        if MOCK_PRINTER:
            logging.info(f"[MOCK] Executing: {' '.join(cmd)}")
            time.sleep(3)
            success = True
            error_msg = None
        else:
            logging.info(f"Executing: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                success = True
                error_msg = None
            else:
                success = False
                error_msg = result.stderr
                
        conn = get_db()
        cursor = conn.cursor()
        if success:
            cursor.execute("UPDATE jobs SET print_status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE job_id = ?", (job_id,))
            logging.info(f"Job {job_id} completed successfully.")
        else:
            cursor.execute("UPDATE jobs SET print_status = 'error', error_log = ? WHERE job_id = ?", (error_msg, job_id))
            logging.error(f"Job {job_id} failed: {error_msg}")
        conn.commit()
        conn.close()
        
    except Exception as e:
        logging.error(f"Exception while printing job {job_id}: {str(e)}")
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE jobs SET print_status = 'error', error_log = ? WHERE job_id = ?", (str(e), job_id))
        conn.commit()
        conn.close()

import datetime
import shutil

def cleanup_temp_files():
    temp_dir = "tmp/kiosk_jobs"
    if not os.path.exists(temp_dir): return
    now = datetime.datetime.now().timestamp()
    for job_id in os.listdir(temp_dir):
        job_path = os.path.join(temp_dir, job_id)
        if os.path.isdir(job_path) and (now - os.path.getmtime(job_path) > 600):
            try:
                shutil.rmtree(job_path)
                logging.info(f"Cleaned up temp files for job: {job_id}")
            except Exception:
                pass

def run_worker():
    logging.info(f"Print manager started. MOCK_PRINTER={MOCK_PRINTER}")
    last_cleanup = 0
    while True:
        try:
            if time.time() - last_cleanup > 60:
                cleanup_temp_files()
                last_cleanup = time.time()
                
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM jobs 
                WHERE payment_status = 'success' AND print_status IN ('waiting', 'queued')
                ORDER BY created_at ASC LIMIT 1
            """)
            job = cursor.fetchone()
            conn.close()
            
            if job:
                process_job(job)
            else:
                time.sleep(2)
        except Exception as e:
            logging.error(f"Worker loop error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    run_worker()
