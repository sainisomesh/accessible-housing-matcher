# Accessible Housing Matcher - Final Deliverable

A complete housing matching system that connects JotForm, Google Sheets, Google Apps Script, and WordPress to help people find accessible housing.

## ⚠️ Important Setup Note

**This system was created and configured on a specific machine/environment. You will need to reconfigure everything for your own machine and setup.**

- **Use AI assistance**: If you encounter issues during setup, use **Cursor AI** or **ChatGPT** to help guide you through the configuration process, as it can get quite complex.
- **Manual tasks required**: There are manual tasks outlined step-by-step below that you'll need to complete (Google Sheets setup, Apps Script deployment, JotForm configuration, etc.).
- **Environment differences**: Paths, ports, database locations, and other system-specific settings may need to be adjusted for your environment.

## 📋 Quick Start

1. **Read the documentation** in order:
   - [Part 1: Overview and Setup](docs/01-OVERVIEW-AND-SETUP.md) - Start here!
   - [Part 2: Google Sheets & Apps Script](docs/02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md)
   - [Part 4: Backend Setup](docs/04-BACKEND-SETUP.md) ⚠️ **REQUIRED** - Frontend needs backend!
   - [Part 3: JotForm & WordPress Integration](docs/03-JOTFORM-AND-WORDPRESS.md)

2. **Follow the step-by-step instructions** in each part

3. **Update configuration values** in the clearly marked config sections

## 📁 Folder Structure

```
accessible-housing-final-deliverable/
├── README.md                          # This file - start here!
├── FILE-GUIDE.md                      # 📖 Explains what every file does
├── QUICK-REFERENCE.md                 # One-page checklist
├── docs/                              # Detailed documentation
│   ├── 01-OVERVIEW-AND-SETUP.md      # Part 1: Overview
│   ├── 02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md  # Part 2: Setup
│   ├── 04-BACKEND-SETUP.md           # Part 4: Backend (REQUIRED)
│   └── 03-JOTFORM-AND-WORDPRESS.md   # Part 3: Integration
├── frontend/                          # React frontend UI
│   ├── src/
│   │   ├── config.js                 # ⚙️ CONFIG: Update URLs here
│   │   ├── App.jsx                   # Main React component
│   │   ├── App.css                   # Styles
│   │   ├── index.css                 # Global styles
│   │   └── main.jsx                  # React entry point
│   ├── index.html                    # HTML template
│   └── package.json                  # Dependencies
├── apps-script/                      # Google Apps Script code
│   └── webhook.gs                    # ⚙️ CONFIG: Update spreadsheet IDs here
├── wordpress/                        # WordPress integration
│   └── housing-matcher-shortcode.php # WordPress plugin
└── backend/                          # Python/FastAPI backend (REQUIRED)
    ├── main.py                       # Main backend server
    ├── models.py                     # Database structure
    ├── utils.py                      # Matching algorithms
    ├── requirements.txt              # Python packages needed
    └── [Other backend files]
```

**📖 New to coding?** See **[FILE-GUIDE.md](FILE-GUIDE.md)** - it explains what every file does in simple terms!

## 🎯 What You Need to Configure

**Only edit these config sections - don't touch the core logic!**

**📖 Not sure what a file does?** Check **[FILE-GUIDE.md](FILE-GUIDE.md)** - it explains every file in simple terms!

### 1. Apps Script (`apps-script/webhook.gs`)
```javascript
// Lines 12-18 - Update these three IDs:
const MASTER_SPREADSHEET_ID = 'YOUR_ID_HERE';
const DATABASE_SPREADSHEET_ID = 'YOUR_ID_HERE';
const MATCHING_SPREADSHEET_ID = 'YOUR_ID_HERE';
```

### 2. Frontend (`frontend/src/config.js`)
```javascript
// Update these URLs:
export const API_URL = 'https://your-backend-url.com'
export const JOTFORM_APPLICANT_URL = 'https://form.jotform.com/YOUR_FORM_ID'
export const JOTFORM_LANDLORD_URL = 'https://form.jotform.com/YOUR_FORM_ID'
export const LOGO_URL = 'https://your-website.com/logo.png'
```

### 3. JotForm Webhook
- Set webhook URL to your Apps Script Web App URL (from Step 2.4 in Part 2)

## 🚀 Implementation Steps

### Step 1: Set Up Google Sheets (15 minutes)
- Create 3 Google Sheets (master, intake, matching)
- Get spreadsheet IDs from URLs
- See [Part 2, Section 1](docs/02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md#step-1-set-up-google-sheets)

### Step 2: Deploy Apps Script (20 minutes)
- Create Apps Script project
- Paste webhook code
- Update spreadsheet IDs
- Deploy as Web App
- Get Web App URL
- See [Part 2, Section 2](docs/02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md#step-2-apps-script-backend-webhook)

### Step 3: Set Up Backend API (30 minutes) ⚠️ **REQUIRED**
- Install Python dependencies
- Configure environment variables
- Run backend locally or deploy to production
- Get backend URL
- See [Part 4: Backend Setup](docs/04-BACKEND-SETUP.md)

### Step 4: Set Up JotForm (15 minutes)
- Create applicant form (and optionally landlord form)
- Add hidden `sheet` field
- Connect webhook to Apps Script URL
- Test submission
- See [Part 3, Section 3](docs/03-JOTFORM-AND-WORDPRESS.md#step-3-jotform-setup--webhook-integration)

### Step 5: Deploy Frontend (30 minutes)
- Update `frontend/src/config.js` with your backend URL
- Build the frontend (`npm install && npm run build`)
- Host the `dist/` folder (GitHub Pages, Netlify, etc.)
- Embed in WordPress (iframe or direct HTML)
- See [Part 3, Section 4](docs/03-JOTFORM-AND-WORDPRESS.md#step-4-frontend-ui--wordpress-integration)
- **💰 FREE Hosting Guide:** See [Free Hosting Setup](docs/FREE-HOSTING-SETUP.md) for step-by-step instructions to host frontend on GitHub Pages (free) and backend on Render (free tier)

## ✅ Testing Checklist

After setup, test the complete flow:

- [ ] Submit test entry in JotForm
- [ ] Verify data appears in intake spreadsheet
- [ ] Verify data appears in master spreadsheet
- [ ] Check that matching sheet is created (for applicants)
- [ ] Test frontend search form
- [ ] Verify matches are displayed
- [ ] Test save/bookmark feature

## 🔧 Troubleshooting

**Data not appearing in sheets?**
- Check Apps Script execution log
- Verify spreadsheet IDs are correct
- Check JotForm webhook URL

**Frontend not loading?**
- Check browser console (F12) for errors
- Verify API_URL in config.js
- Test backend API directly

**IMPORTRANGE not working?**
- Grant permission when Google prompts you
- Check that spreadsheet IDs are correct

See detailed troubleshooting in [Part 3, Section 6](docs/03-JOTFORM-AND-WORDPRESS.md#troubleshooting-common-issues).

## 📚 Documentation Files

- **[Part 1: Overview and Setup](docs/01-OVERVIEW-AND-SETUP.md)** - Start here! Overview, architecture, prerequisites
- **[Part 2: Google Sheets & Apps Script](docs/02-GOOGLE-SHEETS-AND-APPS-SCRIPT.md)** - Setting up sheets and webhook
- **[Part 4: Backend Setup](docs/04-BACKEND-SETUP.md)** ⚠️ **REQUIRED** - Python/FastAPI backend setup and deployment
- **[Part 3: JotForm & WordPress](docs/03-JOTFORM-AND-WORDPRESS.md)** - Form setup and WordPress integration
- **[💰 Free Hosting Setup](docs/FREE-HOSTING-SETUP.md)** - Complete guide for frontend (GitHub Pages) and backend (Render)
- **[🚀 Backend Render Setup](docs/BACKEND-RENDER-SETUP.md)** - **QUICK START** - Simplified guide focusing just on backend deployment (if frontend is already on GitHub Pages)
- **[WordPress Hosting Explanation](docs/WORDPRESS-HOSTING-EXPLANATION.md)** - ⚠️ **IMPORTANT** - Clarifies what WordPress can/cannot host

## 🎓 Skill Level Required

This deliverable is designed for **high-school level coders** who are:
- Comfortable with basic JavaScript/HTML
- Able to copy and paste code
- Familiar with URLs and IDs
- Willing to follow step-by-step instructions

**You don't need to:**
- Understand complex programming concepts
- Modify the core business logic
- Write new code from scratch

## 📝 Important Notes

1. **Only edit config sections** - The core logic is complete and tested
2. **Follow the documentation in order** - Each part builds on the previous one
3. **Test after each step** - Don't wait until the end to test
4. **Save all IDs and URLs** - Keep a list of your spreadsheet IDs, form IDs, and webhook URLs

## 🆘 Getting Help

If you get stuck:
1. Check the troubleshooting sections in each documentation file
2. Review the Apps Script execution log
3. Check browser console for frontend errors
4. Verify all configuration values are correct

## 📦 What's Included

- ✅ Complete Google Apps Script webhook code
- ✅ React frontend with search and matching UI
- ✅ WordPress integration plugin
- ✅ Step-by-step documentation
- ✅ Configuration files with clear instructions
- ✅ Troubleshooting guides

## 🎉 Ready to Start?

Begin with **[Part 1: Overview and Setup](docs/01-OVERVIEW-AND-SETUP.md)** to understand the system architecture and gather your prerequisites.

Good luck with your implementation!

