# Part 4: Backend API Setup (REQUIRED)

## ⚠️ IMPORTANT: Backend is Required

**The frontend requires the backend API to function.** The React frontend makes API calls to the backend to:
- Fetch available housing units
- Submit applicant data
- Calculate and retrieve matches

**You cannot run the frontend without the backend.** This section shows you how to set up and deploy the Python/FastAPI backend.

## Overview

The backend is a **Python FastAPI application** that:
- Receives webhook submissions from JotForm (applicants and landlords)
- Stores data in a SQLite database (or PostgreSQL for production)
- Calculates housing matches using scoring algorithms
- Provides REST API endpoints for the frontend
- Syncs data with Google Sheets via Apps Script

**📖 New to Python or backend code?** See `FILE-GUIDE.md` in the root folder - it explains what each backend file does in simple terms!

## Prerequisites

Before setting up the backend, you need:

1. **Python 3.9 or higher** installed
   - Check: `python3 --version` or `python --version`
   - Download: [python.org](https://www.python.org/downloads/)

2. **pip** (Python package manager) - usually comes with Python

3. **Your Apps Script Web App URL** (from Part 2)
   - You'll need this to sync data from Google Sheets

4. **A hosting service** (for production deployment):
   - **Render.com** (recommended - free tier available)
   - **Railway.app**
   - **Heroku**
   - Or your own server

## Step 1: Local Setup (Development)

### 1.1 Install Dependencies

1. **Navigate to the backend folder:**
   ```bash
   cd accessible-housing-final-deliverable/backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - **On Mac/Linux:**
     ```bash
     source venv/bin/activate
     ```
   - **On Windows:**
     ```bash
     venv\Scripts\activate
     ```

4. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

   This installs:
   - FastAPI (web framework)
   - SQLAlchemy (database ORM)
   - Uvicorn (ASGI server)
   - Requests (for API calls)
   - And other dependencies

### 1.2 Configure Environment Variables

Create a `.env` file in the backend folder:

```bash
# Create .env file
touch .env
```

Add these variables to `.env`:

```env
# Your Google Apps Script Web App URL (from Part 2)
APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec

# CORS origins (comma-separated list of allowed frontend URLs)
# For local development:
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database URL (SQLite for local, PostgreSQL for production)
# Leave empty for default SQLite
DATABASE_URL=
```

**Important:** Replace `YOUR_DEPLOYMENT_ID` with your actual Apps Script Web App URL.

### 1.3 Update Apps Script URL in Code

If you prefer to hardcode the URL (not recommended), edit `utils.py`:

```python
# Find this line:
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL", "YOUR_APPS_SCRIPT_URL_HERE")

# Replace with:
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL", "https://script.google.com/macros/s/YOUR_ID/exec")
```

### 1.4 Initialize the Database

The database will be created automatically when you first run the server. However, if you want to initialize it manually:

```bash
python3 -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

### 1.5 Run the Backend Server

**Option A: Using the start script:**
```bash
chmod +x start_server.sh
./start_server.sh
```

**Option B: Using uvicorn directly:**
```bash
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Option C: Using Python module:**
```bash
python3 -m housingmatcher.main
```

The server will start on **http://localhost:8000**

### 1.6 Verify Backend is Running

1. **Open your browser** and go to: http://localhost:8000
   - You should see: `{"message":"HousingMatcher API is running"}`

2. **Check API documentation:**
   - Go to: http://localhost:8000/docs
   - This shows all available endpoints with interactive testing

3. **Test the units endpoint:**
   - Go to: http://localhost:8000/units
   - You should see a JSON array (may be empty if no units yet)

### 1.7 Sync Data from Google Sheets (Optional)

If you have data in Google Sheets and want to import it:

```bash
# Sync all data from Google Sheets
python3 sync_google_sheets.py

# Or import master units from CSV
python3 import_master_units.py path/to/your/master-sheet.csv
```

---

## Step 2: Connect Frontend to Backend

### 2.1 Update Frontend Configuration

1. **Open `frontend/src/config.js`**

2. **Set the API URL:**
   ```javascript
   // For local development:
   export const API_URL = 'http://localhost:8000'
   
   // For production (after deployment):
   // export const API_URL = 'https://your-backend-api.onrender.com'
   ```

3. **Save the file**

### 2.2 Test the Connection

1. **Start the backend** (if not already running):
   ```bash
   cd backend
   python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend** (in a new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Open the frontend** in your browser (usually http://localhost:5173)

4. **Fill out the form** - you should see matches appear (or an empty state if no units)

5. **Check browser console** (F12) for any errors

---

## Step 3: Production Deployment

For production, you need to deploy the backend to a hosting service so the frontend can access it.

**💰 Want FREE hosting?** See [Free Hosting Setup Guide](FREE-HOSTING-SETUP.md) for complete step-by-step instructions to host both frontend (GitHub Pages) and backend (Render) for free!

### 3.1 Deploy to Render.com (Recommended)

**Render.com offers a free tier and is easy to use.**

1. **Create a Render account:** [render.com](https://render.com)

2. **Create a new Web Service:**
   - Click **New** → **Web Service**
   - Connect your GitHub repository (or use Render's Git)
   - Or upload the backend folder directly

3. **Configure the service:**
   - **Name:** `accessible-housing-backend` (or your choice)
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `backend` (if backend is in a subfolder)

4. **Add Environment Variables:**
   - Click **Environment** tab
   - Add:
     - `APPS_SCRIPT_URL` = Your Apps Script Web App URL
     - `CORS_ORIGINS` = Your frontend URL (e.g., `https://your-site.netlify.app`)
     - `DATABASE_URL` = (Leave empty for SQLite, or add PostgreSQL URL)

5. **Deploy:**
   - Click **Create Web Service**
   - Wait for deployment (5-10 minutes)
   - Copy the service URL (e.g., `https://your-backend.onrender.com`)

6. **Update Frontend Config:**
   - In `frontend/src/config.js`, set:
     ```javascript
     export const API_URL = 'https://your-backend.onrender.com'
     ```

### 3.2 Deploy to Railway

1. **Create Railway account:** [railway.app](https://railway.app)

2. **New Project** → **Deploy from GitHub repo** (or upload)

3. **Configure:**
   - Railway auto-detects Python
   - Add environment variables in the dashboard
   - Railway will provide a URL automatically

4. **Update frontend config** with Railway URL

### 3.3 Deploy to Heroku

1. **Install Heroku CLI:** [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login:**
   ```bash
   heroku login
   ```

3. **Create app:**
   ```bash
   cd backend
   heroku create your-app-name
   ```

4. **Set environment variables:**
   ```bash
   heroku config:set APPS_SCRIPT_URL=your_url
   heroku config:set CORS_ORIGINS=your_frontend_url
   ```

5. **Deploy:**
   ```bash
   git push heroku main
   ```

6. **Get URL:**
   ```bash
   heroku info
   ```

### 3.4 Using Your Own Server

If you have a VPS or server:

1. **SSH into your server**

2. **Install Python and dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Upload backend files** (via SCP, FTP, or Git)

4. **Set up virtual environment and install:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Set environment variables:**
   ```bash
   export APPS_SCRIPT_URL=your_url
   export CORS_ORIGINS=your_frontend_url
   ```

6. **Run with a process manager** (PM2, systemd, or supervisor):
   ```bash
   # Using PM2:
   pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name housing-backend
   
   # Or using systemd (create a service file)
   ```

7. **Set up reverse proxy** (nginx or Apache) to handle HTTPS

---

## Step 4: Database Setup

### 4.1 SQLite (Default - Good for Development)

SQLite is used by default. The database file (`housingmatcher.db`) is created automatically when you first run the server.

**Pros:**
- No setup required
- Good for development and small deployments
- File-based (easy to backup)

**Cons:**
- Not ideal for high-traffic production
- Limited concurrent writes

### 4.2 PostgreSQL (Recommended for Production)

For production, use PostgreSQL for better performance and reliability.

1. **Set up PostgreSQL:**
   - Use a managed service (Render, Railway, Heroku Postgres)
   - Or install on your server

2. **Get connection string:**
   - Format: `postgresql://user:password@host:port/database`

3. **Set environment variable:**
   ```bash
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

4. **Update `database.py`** if needed to handle PostgreSQL-specific settings

---

## Step 5: API Endpoints Reference

The backend provides these endpoints:

### Health Check
- **GET** `/` - Returns API status
- Response: `{"message": "HousingMatcher API is running"}`

### Units
- **GET** `/units` - List all housing units
- Returns: Array of unit objects with all details

### Applicants
- **GET** `/applicants` - List all applicants
- Returns: Array of applicant objects

### Matching
- **GET** `/match/{applicant_id}` - Get matches for an applicant
- Returns: `{"matches": [...], "applicant": {...}}`
- Each match includes: `unit_id`, `score`, `reasons`

### Webhooks
- **POST** `/webhook/applicant` - Receive applicant submissions from JotForm
- **POST** `/webhook/landlord` - Receive landlord submissions from JotForm
- Body: JotForm webhook payload

### API Documentation
- **GET** `/docs` - Interactive API documentation (Swagger UI)
- **GET** `/redoc` - Alternative API documentation

---

## Step 6: Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'housingmatcher'"

**Solution:**
- Make sure you're running from the correct directory
- Install dependencies: `pip install -r requirements.txt`
- If using virtual environment, make sure it's activated

### Problem: "Port 8000 already in use"

**Solution:**
- Use a different port: `uvicorn main:app --port 8001`
- Or kill the process using port 8000

### Problem: Frontend can't connect to backend

**Solutions:**
- Check backend is running: `curl http://localhost:8000`
- Verify `API_URL` in `frontend/src/config.js` is correct
- Check CORS settings in `main.py`
- Look for errors in browser console (F12)

### Problem: "CORS policy" errors

**Solution:**
- Update `CORS_ORIGINS` in `.env` or `main.py`
- Add your frontend URL to the allowed origins list
- For development, you can temporarily use `["*"]` (not recommended for production)

### Problem: Database errors

**Solution:**
- Make sure the database file has write permissions
- For PostgreSQL, verify connection string is correct
- Check database logs for specific errors

### Problem: Apps Script sync not working

**Solution:**
- Verify `APPS_SCRIPT_URL` is correct in environment variables
- Test the Apps Script URL directly in browser
- Check Apps Script execution log for errors
- Make sure Apps Script is deployed as "Web app" (not API)

---

## Step 7: Production Checklist

Before going live, ensure:

- [ ] Backend is deployed and accessible
- [ ] Environment variables are set correctly
- [ ] CORS origins include your frontend URL
- [ ] Database is set up (SQLite or PostgreSQL)
- [ ] Frontend `config.js` points to production backend URL
- [ ] Apps Script URL is correct
- [ ] HTTPS is enabled (for production)
- [ ] Error logging is configured
- [ ] Database backups are set up (for PostgreSQL)
- [ ] Monitoring is in place (optional but recommended)

---

## Next Steps

Once your backend is running:

1. **Test all endpoints** using `/docs` interface
2. **Sync data from Google Sheets** (if needed)
3. **Update frontend config** with backend URL
4. **Test the complete flow** (form submission → matching)
5. **Deploy frontend** and verify it connects to backend

The backend is the **core of the system** - make sure it's running before testing the frontend!

