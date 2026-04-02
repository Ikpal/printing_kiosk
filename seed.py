import sqlite3
import os

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./db/kiosk.db").replace("sqlite:///", "")

def seed_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables if not exist based on schema
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS jobs (
          job_id       TEXT PRIMARY KEY,
          filename     TEXT,
          file_path    TEXT,
          pages        INTEGER,
          copies       INTEGER,
          page_range   TEXT,
          color_mode   TEXT CHECK(color_mode IN ('bw','color')),
          duplex       BOOLEAN,
          total_pages  INTEGER,
          amount_inr   REAL,
          txn_id       TEXT,
          payment_status TEXT DEFAULT 'pending',
          print_status TEXT DEFAULT 'waiting',
          error_log    TEXT,
          created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          completed_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pricing (
          mode TEXT PRIMARY KEY,
          price_per_page REAL
        );

        CREATE TABLE IF NOT EXISTS admin_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          action TEXT,
          job_id TEXT,
          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Seed pricing
    default_pricing = [
        ('bw', 1.50),           # Single side B&W
        ('bw_duplex', 2.50),    # Double side B&W
        ('color', 8.00),        # Single side Color
        ('color_duplex', 14.00) # Double side Color
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO pricing (mode, price_per_page) 
        VALUES (?, ?)
    """, default_pricing)

    conn.commit()
    conn.close()
    print("Database seeded successfully with default pricing.")

if __name__ == "__main__":
    seed_db()
