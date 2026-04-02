import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db/kiosk.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_jwt_key")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")
MOCK_PRINTER = os.getenv("MOCK_PRINTER", "true").lower() == "true"
KIOSK_IDLE_TIMEOUT_SEC = int(os.getenv("KIOSK_IDLE_TIMEOUT_SEC", 180))

UPI_ID = os.getenv("UPI_ID", "masterrudra@upi")
UPI_NAME = os.getenv("UPI_NAME", "PrintBuddy")

# Constants
MAX_FILE_SIZE_MB = 20
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "image/jpeg": ".jpg",
    "image/png": ".png"
}

# Ensure directories
os.makedirs("tmp/kiosk_jobs", exist_ok=True)
os.makedirs("db", exist_ok=True)
