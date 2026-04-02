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
from ..config import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET, RAZORPAY_WEBHOOK_SECRET

try:
    import razorpay
except ImportError:
    razorpay = None

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
    
    if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and razorpay:
        # Create Razorpay Payment Link
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        try:
            link_data = {
                "amount": int(amount_inr * 100), # amount in paise
                "currency": "INR",
                "reference_id": txn_id,
                "description": f"Printing Kiosk Job {req.job_id[:8]}",
                "notes": {
                    "job_id": req.job_id
                }
            }
            payment_link = client.payment_link.create(link_data)
            payment_url = payment_link['short_url']
            razorpay_link_id = payment_link['id']
            
            txn_id = razorpay_link_id
            qr_b64 = generate_qr_b64(payment_url)
            upi_string = payment_url
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Razorpay Error: {str(e)}")
    else:
        # Phase 1: Mock UPI String
        upi_string = f"upi://pay?pa=test@upi&am={amount_inr}&tn={txn_id}"
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

@router.post("/webhook")
async def payment_webhook(request: Request):
    if not RAZORPAY_WEBHOOK_SECRET:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")
        
    body = await request.body()
    signature = request.headers.get('x-razorpay-signature')
    
    if not signature:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    # Verify Signature
    expected_sig = hmac.new(
        bytes(RAZORPAY_WEBHOOK_SECRET, 'utf-8'),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_sig, signature):
        raise HTTPException(status_code=400, detail="Invalid signature")
        
    data = json.loads(body.decode('utf-8'))
    
    if data.get('event') == 'payment_link.paid':
        payment_link = data['payload']['payment_link']['entity']
        txn_id = payment_link['id']
        job_id = payment_link['notes'].get('job_id')
        
        if txn_id and job_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET payment_status = 'success', print_status = 'waiting' WHERE txn_id = ?", (txn_id,))
            conn.commit()
            conn.close()
            
    return {"status": "ok"}
