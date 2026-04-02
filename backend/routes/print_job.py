from fastapi import APIRouter, HTTPException
from ..database import get_db_connection
from ..models import CalculateRequest, CalculateResponse, PrintStatusResponse

router = APIRouter()

@router.post("/calculate", response_model=CalculateResponse)
async def calculate_price(req: CalculateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT total_pages FROM jobs WHERE job_id = ?", (req.job_id,))
    job = cursor.fetchone()
    if not job or not job['total_pages']:
        conn.close()
        raise HTTPException(status_code=404, detail="Job not found or preview not generated")
        
    total_doc_pages = job['total_pages']
    
    if req.page_range.lower() == 'all':
        pages_to_print = total_doc_pages
    else:
        try:
            parts = req.page_range.split('-')
            start = int(parts[0])
            end = int(parts[1]) if len(parts) > 1 else start
            pages_to_print = (end - start) + 1
            if pages_to_print < 1 or start < 1 or end > total_doc_pages:
                raise ValueError()
        except Exception:
            conn.close()
            raise HTTPException(status_code=400, detail="Invalid page range")
            
    total_printed_pages = pages_to_print * req.copies
    
    mode = f"{req.color_mode}_duplex" if req.duplex else req.color_mode
    
    cursor.execute("SELECT price_per_page FROM pricing WHERE mode = ?", (mode,))
    pricing = cursor.fetchone()
    if not pricing:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Pricing not configured for {mode}")
        
    if req.duplex:
        sheets = (total_printed_pages + 1) // 2
        price_inr = sheets * pricing['price_per_page']
    else:
        price_inr = total_printed_pages * pricing['price_per_page']

    cursor.execute("""
        UPDATE jobs 
        SET copies = ?, page_range = ?, color_mode = ?, duplex = ?, amount_inr = ?
        WHERE job_id = ?
    """, (req.copies, req.page_range, req.color_mode, req.duplex, price_inr, req.job_id))
    conn.commit()
    conn.close()
    
    return {"total_pages": total_printed_pages, "price_inr": price_inr}

@router.post("/start")
async def start_print(job_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payment_status FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    if not row or row['payment_status'] != 'success':
        conn.close()
        raise HTTPException(status_code=400, detail="Payment not successful")
        
    cursor.execute("UPDATE jobs SET print_status = 'queued' WHERE job_id = ?", (job_id,))
    conn.commit()
    conn.close()
    return {"status": "queued"}

@router.get("/status/{job_id}", response_model=PrintStatusResponse)
async def get_print_status(job_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT print_status, error_log FROM jobs WHERE job_id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {"status": row['print_status'], "pages_done": 0, "error": row['error_log']}
