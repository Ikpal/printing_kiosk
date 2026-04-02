import sqlite3
import os
from .config import DATABASE_URL

DB_PATH = DATABASE_URL.replace("sqlite:///", "")

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH) or '.', exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
