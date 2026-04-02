# College Printing Kiosk System

A complete kiosk system for self-service printing, built with FastAPI, React (Vite), and Python background workers.

## Prerequisites
- Python 3.10+
- Node.js 18+
- CUPS (Linux/Raspberry Pi) or a mock printer setup (Windows)

## Installation

### 1. Backend & Worker
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
```

### 2. Frontend & Admin
```bash
# Frontend Kiosk
cd frontend
npm install
npm run build

# Admin Panel
cd ../admin
npm install
npm run build
```

## Running the System

Start both the backend server and the print manager worker:
```bash
bash run.sh
```

## Kiosk Mode (Chromium)
To run the frontend in kiosk mode on a Raspberry Pi:
```bash
chromium-browser --kiosk --incognito http://localhost:8000
```

## CUPS Printer Configuration
1. Install CUPS: `sudo apt install cups`
2. Add your printer via the CUPS web interface (`http://localhost:631`)
3. Set the newly added printer as the default printer in CUPS. The `lp` command will use the default printer automatically.
