# Part 1: Overview and Setup

## ⚠️ Important Setup Note

**This system was created and configured on a specific machine/environment. You will need to reconfigure everything for your own machine and setup.**

- **Use AI assistance**: If you encounter issues during setup, use **Cursor AI** or **ChatGPT** to help guide you through the configuration process, as it can get quite complex.
- **Manual tasks required**: There are manual tasks outlined step-by-step below that you'll need to complete (Google Sheets setup, Apps Script deployment, JotForm configuration, etc.).
- **Environment differences**: Paths, ports, database locations, and other system-specific settings may need to be adjusted for your environment.

## What This Tool Does

The Accessible Housing Matcher is a web-based tool that helps people find accessible housing that matches their specific needs. Users fill out a form with their income, location, household size, and accessibility requirements. The system then automatically matches them with available housing units and displays the results in real-time.

**Data Flow:**
1. Users submit information via JotForm
2. JotForm sends data to Google Apps Script (webhook)
3. Apps Script writes data to Google Sheets
4. The frontend UI reads from Google Sheets (or a backend API) and displays matches
5. Each applicant gets their own matching sheet in Google Sheets

## Architecture at a Glance

Here's what each component does:

- **JotForm Intake Forms**: Two forms - one for applicants (people looking for housing) and one for landlords (people listing properties)
- **Google Sheets - Master Housing Sheet**: Contains all available housing units with details like address, rent, accessibility features, and contact information
- **Google Sheets - Applicant Intake Sheet**: Receives submissions from the applicant JotForm
- **Google Sheets - Matching Spreadsheet**: Creates one sheet per applicant showing their potential matches
- **Google Apps Script Webhook**: Receives JotForm submissions, writes to sheets, and creates matching sheets
- **Frontend UI**: A React-based search and matching interface that can be embedded in WordPress

## Prerequisites

Before you start, make sure you have:

1. **A Google Account** with access to:
   - Google Sheets (to create and manage spreadsheets)
   - Google Apps Script (to deploy the webhook)

2. **A JotForm Account** (free tier works fine)
   - You'll need to create two forms: one for applicants, one for landlords

3. **WordPress Admin Access** (or someone who can edit pages and add custom HTML)
   - You'll need to embed the frontend UI in a WordPress page

4. **Python 3.9 or higher** (for the backend)
   - Check: `python3 --version` or `python --version`
   - Download: [python.org](https://www.python.org/downloads/)

5. **Basic Coding Knowledge**:
   - Comfortable copying and pasting code
   - Understanding of URLs and IDs
   - Basic HTML/CSS knowledge (helpful but not required)
   - **Don't worry if you're new to coding!** See `FILE-GUIDE.md` for explanations of every file.

## Configuration Cheat Sheet

You'll need to collect these IDs and URLs throughout the setup process. Keep this list handy:

| Item | Where to Find It | Example |
|------|------------------|---------|
| **MASTER_SPREADSHEET_ID** | From your master housing sheet URL | `19is049RiNyvLRpo0kpU1Xub8SaI_9XkO5a7Y2ILkC5U` |
| **DATABASE_SPREADSHEET_ID** | From your JotForm intake sheet URL | `19FO0fWMxrCjPXLIXJYAAipJAgqpN79yyfagv5IPPiHg` |
| **MATCHING_SPREADSHEET_ID** | From your matching spreadsheet URL | `1N2SgUB7ef8zexv2mxHHNztRhD-iy01qvbf6yv6iBUqA` |
| **JotForm Applicant Form ID** | From JotForm form settings | `252946057108056` |
| **JotForm Landlord Form ID** | From JotForm form settings | `252946240036050` |
| **Apps Script Web App URL** | After deploying Apps Script (Step 2) | `https://script.google.com/macros/s/.../exec` |
| **Backend API URL** (if using) | Your deployed backend URL | `https://your-api.onrender.com` |

**Important:** You only need to change values in the **config sections** of the code files. The core logic should remain untouched.

## Quick Start Checklist

Follow these steps in order:

- [ ] **Step 1**: Set up Google Sheets (see Part 2)
- [ ] **Step 2**: Deploy Apps Script webhook (see Part 2)
- [ ] **Step 3**: Set up backend API (see Part 4) ⚠️ **REQUIRED**
- [ ] **Step 4**: Set up JotForm and connect webhook (see Part 3)
- [ ] **Step 5**: Deploy frontend and embed in WordPress (see Part 3)
- [ ] **Step 6**: Test the complete flow

## ⚠️ Important: Backend is Required

**The frontend cannot work without the backend API.** The React frontend makes API calls to fetch units, submit applicants, and get matches. You **must** set up the backend (see Part 4) before the frontend will function.

## Next Steps

Continue to **Part 2: Google Sheets & Apps Script Setup** to begin the implementation, then proceed to **Part 4: Backend Setup** which is required for the system to work.

