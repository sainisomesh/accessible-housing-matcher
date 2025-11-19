# File Guide - What Each File Does

This guide explains every file in this package in simple, non-technical terms. Use this as a reference when you're not sure what a file does.

## 📁 Folder Structure Overview

```
accessible-housing-final-deliverable/
├── README.md                    # Start here! Main instructions
├── FILE-GUIDE.md               # This file - explains all files
├── QUICK-REFERENCE.md          # One-page checklist
├── docs/                       # Detailed step-by-step guides
├── frontend/                   # The user interface (what users see)
├── backend/                    # The server (handles data and matching)
├── apps-script/                # Google Apps Script code
└── wordpress/                  # WordPress plugin
```

---

## 📄 Main Documentation Files

### `README.md`
**What it is:** The main instruction manual. Start here!
**What it does:** Gives you an overview of the entire system and points you to the detailed guides.
**When to use it:** Read this first to understand the big picture.

### `FILE-GUIDE.md` (This file)
**What it is:** A dictionary of all files in the package.
**What it does:** Explains what each file does in simple terms.
**When to use it:** When you see a file name and don't know what it does.

### `QUICK-REFERENCE.md`
**What it is:** A one-page cheat sheet.
**What it does:** Lists all the IDs and URLs you need to configure, plus a quick testing checklist.
**When to use it:** Keep this open while setting up - use it as a checklist.

### `DELIVERABLE-SUMMARY.md`
**What it is:** An overview of what's included in this package.
**What it does:** Summarizes all the components for reference.
**When to use it:** Optional reading - helps you understand the complete package.

---

## 📚 Documentation Files (`docs/` folder)

### `docs/01-OVERVIEW-AND-SETUP.md`
**What it is:** Part 1 of the setup guide.
**What it does:** Explains what the system does, how it works, and what you need before starting.
**When to use it:** Read this first to understand the system architecture.

### `docs/02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md`
**What it is:** Part 2 of the setup guide.
**What it does:** Step-by-step instructions for setting up Google Sheets and the Apps Script webhook.
**When to use it:** Follow this after reading Part 1.

### `docs/04-BACKEND-SETUP.md`
**What it is:** Part 4 of the setup guide (backend setup).
**What it does:** Detailed instructions for setting up and deploying the Python backend server.
**When to use it:** Follow this after Part 2 - the backend is required for the frontend to work.

### `docs/03-JOTFORM-AND-WORDPRESS.md`
**What it is:** Part 3 of the setup guide.
**What it does:** Instructions for setting up JotForm forms and embedding the frontend in WordPress.
**When to use it:** Follow this after setting up the backend.

---

## 🎨 Frontend Files (`frontend/` folder)

The frontend is what users see and interact with - the search form and match results.

### `frontend/package.json`
**What it is:** A list of required software packages.
**What it does:** Tells the computer what additional code libraries the frontend needs to run.
**When to use it:** You don't edit this - the computer reads it when you run `npm install`.

### `frontend/index.html`
**What it is:** The main HTML page structure.
**What it does:** Creates the basic webpage that holds the React application.
**When to use it:** You don't need to edit this - it's just the container.

### `frontend/src/config.js` ⚙️ **EDIT THIS FILE**
**What it is:** Configuration file with URLs and settings.
**What it does:** Stores the addresses where the frontend should look for the backend API and JotForm links.
**When to use it:** **You MUST edit this file** - replace the example URLs with your actual URLs:
- `API_URL` - Your backend server address
- `JOTFORM_APPLICANT_URL` - Your applicant form link
- `JOTFORM_LANDLORD_URL` - Your landlord form link
- `LOGO_URL` - Your organization's logo (optional)

### `frontend/src/App.jsx`
**What it is:** The main React component - the brain of the frontend.
**What it does:** Contains all the logic for the search form, matching display, and save feature.
**When to use it:** You don't need to edit this unless you want to customize the functionality.

### `frontend/src/App.css`
**What it is:** Styling file - makes things look pretty.
**What it does:** Controls colors, fonts, spacing, and layout of the frontend.
**When to use it:** Edit this if you want to change colors or styling to match your brand.

### `frontend/src/index.css`
**What it is:** Global styling file.
**What it does:** Sets basic styles that apply to the entire page.
**When to use it:** Usually don't need to edit this.

### `frontend/src/main.jsx`
**What it is:** The entry point that starts the React app.
**What it does:** Tells the browser to load and display the React application.
**When to use it:** You don't need to edit this.

---

## ⚙️ Backend Files (`backend/` folder)

The backend is the server that handles data, calculations, and API requests. It's written in Python.

### `backend/requirements.txt` ⚙️ **IMPORTANT**
**What it is:** A list of Python packages needed.
**What it does:** Lists all the code libraries the backend needs (like FastAPI, SQLAlchemy, etc.).
**When to use it:** The computer reads this when you run `pip install -r requirements.txt` to install everything.

### `backend/runtime.txt`
**What it is:** Specifies which Python version to use.
**What it does:** Tells hosting services (like Render) which Python version to install.
**When to use it:** You might need to edit this if your hosting service requires a specific Python version.

### `backend/Procfile`
**What it is:** Instructions for how to start the server.
**What it does:** Tells hosting services (like Heroku) the command to run when starting your app.
**When to use it:** Usually don't need to edit this.

### `backend/render.yaml`
**What it is:** Configuration file for Render.com hosting.
**What it does:** Tells Render.com how to build and deploy your backend.
**When to use it:** Only needed if deploying to Render.com.

### `backend/start_server.sh`
**What it is:** A script to start the backend server easily.
**What it does:** Runs the command to start the server (saves you from typing the long command).
**When to use it:** Run this to start the backend locally: `./start_server.sh`

### `backend/__init__.py`
**What it is:** Makes Python treat the folder as a package.
**What it does:** Allows Python to import files from this folder.
**When to use it:** You don't need to edit this - it's just a marker file.

### `backend/README.md`
**What it is:** Backend-specific setup instructions.
**What it does:** Explains how to set up and run the backend server.
**When to use it:** Read this when setting up the backend (also see Part 4 documentation).

### `backend/main.py` ⚙️ **CORE FILE**
**What it is:** The main backend application file.
**What it does:** 
- Creates the web server
- Defines all API endpoints (like `/units`, `/match`, etc.)
- Handles webhook requests from JotForm
- Connects everything together
**When to use it:** You don't need to edit this unless you want to add new features or change API behavior.

### `backend/models.py` ⚙️ **CORE FILE**
**What it is:** Database structure definitions.
**What it does:** Defines what data tables look like (Unit, Applicant, MasterUnit) and what fields they have.
**When to use it:** You don't need to edit this unless you want to change the database structure.

### `backend/database.py` ⚙️ **CORE FILE**
**What it is:** Database connection setup.
**What it does:** Creates the connection to the database (SQLite or PostgreSQL) and sets up the database engine.
**When to use it:** You might need to edit this if using PostgreSQL instead of SQLite.

### `backend/utils.py` ⚙️ **CORE FILE**
**What it is:** Helper functions and matching algorithms.
**What it does:** 
- Contains the matching logic (how scores are calculated)
- Parses data from JotForm
- Handles communication with Google Apps Script
- Utility functions for data processing
**When to use it:** You might need to edit the `APPS_SCRIPT_URL` here if you don't use environment variables.

### `backend/sync_google_sheets.py` 🔧 **UTILITY**
**What it is:** Script to import data from Google Sheets.
**What it does:** Reads data from your Google Sheets and imports it into the backend database.
**When to use it:** Run this when you want to sync data from Google Sheets to the database:
```bash
python3 sync_google_sheets.py
```

### `backend/import_master_units.py` 🔧 **UTILITY**
**What it is:** Script to import master units from a CSV file.
**What it does:** Reads a CSV file (like an exported Google Sheet) and imports housing units into the database.
**When to use it:** Run this to import your master housing database:
```bash
python3 import_master_units.py path/to/your/file.csv
```

### `backend/backfill_google_sheets.py` 🔧 **UTILITY**
**What it is:** Script to send existing database data back to Google Sheets.
**What it does:** Takes data from the database and writes it to Google Sheets (opposite of sync).
**When to use it:** Run this if you need to update Google Sheets with data from your database.

---

## 📜 Apps Script Files (`apps-script/` folder)

### `apps-script/webhook.gs` ⚙️ **EDIT THIS FILE**
**What it is:** Google Apps Script code that receives JotForm submissions.
**What it does:** 
- Receives data when someone submits a JotForm
- Writes that data to Google Sheets
- Creates matching sheets for applicants
**When to use it:** **You MUST edit this file** - replace the three spreadsheet IDs at the top:
- `MASTER_SPREADSHEET_ID` - Your master housing sheet ID
- `DATABASE_SPREADSHEET_ID` - Your JotForm intake sheet ID
- `MATCHING_SPREADSHEET_ID` - Your matching spreadsheet ID

---

## 🔌 WordPress Files (`wordpress/` folder)

### `wordpress/housing-matcher-shortcode.php` ⚙️ **EDIT THIS FILE**
**What it is:** WordPress plugin file.
**What it does:** Creates shortcodes you can use in WordPress to display housing units and matches.
**When to use it:** 
- Upload this to your WordPress site as a plugin
- Edit the `api_url` setting to point to your backend
- Use shortcodes like `[housing_units]` in WordPress pages

---

## 🎯 Quick Reference: Which Files to Edit

**You only need to edit these files:**

1. **`apps-script/webhook.gs`** - Replace 3 spreadsheet IDs
2. **`frontend/src/config.js`** - Replace 4 URLs (API, JotForm forms, logo)
3. **`wordpress/housing-matcher-shortcode.php`** - Replace API URL (if using WordPress plugin)
4. **Backend environment variables** - Set `APPS_SCRIPT_URL` and `CORS_ORIGINS` (in `.env` file or hosting dashboard)

**Everything else should work as-is!**

---

## 📖 File Types Explained

### `.md` files (Markdown)
- These are documentation files
- Read them in any text editor or on GitHub
- They contain instructions and explanations

### `.py` files (Python)
- These are Python code files
- They contain the backend logic
- You don't need to edit them unless customizing

### `.jsx` files (React/JavaScript)
- These are React component files
- They contain the frontend code
- You don't need to edit them unless customizing

### `.css` files (Stylesheets)
- These control how things look
- Edit these if you want to change colors/styling

### `.json` files (Configuration)
- These contain configuration data
- Usually don't need to edit

### `.gs` files (Google Apps Script)
- This is Google Apps Script code
- You need to edit the IDs in `webhook.gs`

### `.php` files (WordPress)
- This is PHP code for WordPress
- You need to edit the API URL in the plugin

### `.txt` files (Text)
- Usually configuration or requirements lists
- `requirements.txt` lists Python packages needed

### `.sh` files (Shell Script)
- Scripts that run commands
- `start_server.sh` starts the backend server

### `.yaml` / `.yml` files (Configuration)
- Configuration files for hosting services
- Usually don't need to edit

---

## ❓ Still Confused?

If you're not sure what a file does:

1. **Check this guide** - Look up the file name above
2. **Check the README** - It explains the overall structure
3. **Check the documentation** - Parts 1-4 explain how to use everything
4. **Don't edit files you're not sure about** - Most files work as-is!

Remember: **You only need to edit configuration files** (the ones marked with ⚙️). Everything else should work without changes.

