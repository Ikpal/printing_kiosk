from pydantic import BaseModel
from typing import Optional

class CalculateRequest(BaseModel):
    job_id: str
    copies: int
    page_range: str
    color_mode: str
    duplex: bool

class CalculateResponse(BaseModel):
    total_pages: int
    price_inr: float

class PaymentCreateRequest(BaseModel):
    job_id: str

class PaymentCreateResponse(BaseModel):
    qr_data: str
    upi_string: str
    txn_id: str

class PaymentStatusResponse(BaseModel):
    status: str

class PrintStatusResponse(BaseModel):
    status: str
    pages_done: int
    error: Optional[str] = None
