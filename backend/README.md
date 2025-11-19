# Backend API (Python/FastAPI)

This is the  backend API for the Accessible Housing Matcher. The system can work with just Google Sheets and Apps Script, but this backend provides:

- Real-time matching calculations
- RESTful API endpoints
- Better performance with large datasets
- More complex matching algorithms

## ⚠️ Important Setup Note

**This backend was created and configured on a specific machine/environment. You will need to reconfigure everything for your own machine and setup.**

- **Use AI assistance**: If you encounter issues during setup, use **Cursor AI** or **ChatGPT** to help guide you through the configuration process, as it can get quite complex.
- **Manual tasks required**: There are manual tasks outlined step-by-step below that you'll need to complete (environment variables, database setup, deployment configuration, etc.).
- **Environment differences**: Paths, ports, database locations, Python versions, and other system-specific settings may need to be adjusted for your environment.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Google Apps Script deployment URL (for syncing data)
APPS_SCRIPT_URL=https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,https://your-wordpress-site.com

# Database (SQLite by default, or set DATABASE_URL for PostgreSQL)
DATABASE_URL=sqlite:///./housingmatcher.db
```

### Update Apps Script URL

In `utils.py`, find:
```python
APPS_SCRIPT_URL = os.getenv("APPS_SCRIPT_URL", "YOUR_APPS_SCRIPT_URL_HERE")
```

Replace with your actual Apps Script Web App URL.

## 🚀 Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python -m uvicorn housingmatcher.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Or use the start script:
   ```bash
   ./start_server.sh
   ```

3. **Test the API:**
   - Open http://localhost:8000/docs for API documentation
   - Test endpoint: http://localhost:8000/

## 📦 Deployment

### Option 1: Render.com (Recommended)

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn housingmatcher.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables in Render dashboard
5. Deploy

### Option 2: Railway

1. Connect GitHub repository
2. Railway will auto-detect Python
3. Add environment variables
4. Deploy

### Option 3: Heroku

1. Install Heroku CLI
2. Run:
   ```bash
   heroku create your-app-name
   heroku config:set APPS_SCRIPT_URL=your_url
   git push heroku main
   ```

## 📡 API Endpoints

- `GET /` - Health check
- `GET /units` - List all housing units
- `GET /applicants` - List all applicants
- `GET /match/{applicant_id}` - Get matches for an applicant
- `POST /webhook/applicant` - Receive applicant submissions from JotForm
- `POST /webhook/landlord` - Receive landlord submissions from JotForm

See `/docs` endpoint for full API documentation.

## 🔄 Syncing with Google Sheets

The backend can sync data from Google Sheets using the Apps Script URL:

```bash
python -m housingmatcher.sync_google_sheets
```

Or use the sync endpoint (if implemented).

## 📝 Notes

- The backend uses SQLite by default (good for development)
- For production, consider PostgreSQL (set `DATABASE_URL`)
- The database file (`housingmatcher.db`) is created automatically
- Make sure to set proper CORS origins for production

