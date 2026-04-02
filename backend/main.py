from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .routes import upload, preview, print_job, payment, admin, mobile

app = FastAPI(title="College Printing Kiosk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(preview.router, prefix="/preview", tags=["Preview"])
app.include_router(print_job.router, prefix="/print", tags=["Print"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(mobile.router, prefix="/mobile", tags=["Mobile"])

@app.get("/")
def read_root():
    return {"message": "Kiosk API is running"}
