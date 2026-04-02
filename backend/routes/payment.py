from fastapi import APIRouter, Request, HTTPException
import uuid
import qrcode
import io
import base64
import json
import hmac
import hashlib
from ..database import get_db_connection
from ..models import PaymentCreateRequest, PaymentCreateResponse, PaymentStatusResponse
from ..config import UPI_ID, UPI_NAME

router = APIRouter()

def generate_qr_b64(data: str):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

@router.post("/create", response_model=PaymentCreateResponse)
async def create_payment(req: PaymentCreateRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT amount_inr FROM jobs WHERE job_id = ?", (req.job_id,))
    job = cursor.fetchone()
    if not job or job['amount_inr'] is None:
        conn.close()
        raise HTTPException(status_code=400, detail="Job not ready for payment")
        
    amount_inr = float(job['amount_inr'])
    txn_id = str(uuid.uuid4())
    
    # Generate exact UPI intent string
    upi_string = f"upi://pay?pa={UPI_ID}&pn={UPI_NAME}&am={amount_inr}&cu=INR&tn={txn_id}"
    qr_b64 = generate_qr_b64(upi_string)
    
    cursor.execute("UPDATE jobs SET txn_id = ?, payment_status = 'pending' WHERE job_id = ?", (txn_id, req.job_id))
    conn.commit()
    conn.close()
    
    return {
        "qr_data": f"data:image/png;base64,{qr_b64}",
        "upi_string": upi_string,
        "txn_id": txn_id
    }

@router.get("/status/{txn_id}", response_model=PaymentStatusResponse)
async def get_payment_status(txn_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT payment_status FROM jobs WHERE txn_id = ?", (txn_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    return {"status": row['payment_status']}

@router.post("/simulate/{txn_id}")
async def simulate_payment(txn_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE jobs SET payment_status = 'success', print_status = 'waiting' WHERE txn_id = ?", (txn_id,))
    conn.commit()
    conn.close()
    return {"status": "success"}

