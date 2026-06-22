
# ✅LinkedIn Job Filter - Automation Tool

A web application that filters LinkedIn job postings and automatically records them in Google Sheets.

## 📋 Project Overview

- **Purpose**: Automating custom filtering for LinkedIn job searches
  - Uploads JSON files scraped using the Apify service to protect linkedin accounts
  - Executes custom filtering
    - Including lower/upper salary bounds, minimum experience, excluding SC clearance requirements, and excluding managerial roles 
  - Integrates with Google Spreadsheet for automated logging

- **Tech Stack**:
  - **Frontend**: Vite + React (JS)
  - **Backend**: FastAPI (Python)
  - **Data Storage**: Google Sheets API

### Installation & Setup

#### 1. Backend Setup
Install Python dependencies and start the server:
```bash
cd backend
source ../venv/bin/activate
pip install -r requirements.txt
python main.py
```

#### 2. Frontend Setup
Install Node.js dependencies and start the development server:
```bash
cd frontend
npm install
npm run dev
```

