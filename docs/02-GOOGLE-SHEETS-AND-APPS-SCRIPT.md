# Part 2: Google Sheets & Apps Script Setup

## Step 1: Set Up Google Sheets

You'll need to create three Google Sheets. Each serves a specific purpose in the system.

### 1.1 Create the Master Housing Spreadsheet

This sheet contains all available housing units from your master database.

**Steps:**

1. Go to [Google Sheets](https://sheets.google.com)
2. Click **Blank** to create a new spreadsheet
3. Name it something like "Master Housing Database" or "CYC - Accessible Housing"
4. **Set up the header row** (Row 1) with these exact column names:
   - `Unit Number`
   - `Complex/Apartment`
   - `Landlord Name`
   - `Landlord Contact`
   - `Response Status`
   - `Is Available? (Y /N)`
   - `Address`
   - `City`
   - `Zip Code`
   - `Rent`
   - `Income Range`
   - `Age Range`
   - `Accessibility Features`
   - `Transportation`
   - `Stores`
   - `Building Features`
   - `Apartment Features`
   - `Notes`

5. **Get the Spreadsheet ID:**
   - Look at the URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copy the long string between `/d/` and `/edit`
   - This is your `MASTER_SPREADSHEET_ID`
   - **Save this ID** - you'll need it for the Apps Script

6. **Populate with your housing data** (or leave empty for now - you can import data later)

### 1.2 Create the JotForm Intake Spreadsheet

This sheet receives submissions from your JotForm.

**Steps:**

1. Create a new Google Sheet
2. Name it something like "JotForm Intake" or "Accessible Housing Database"
3. **Leave it empty** - the Apps Script will automatically create columns based on what JotForm sends
4. **Get the Spreadsheet ID** from the URL (same process as above)
   - This is your `DATABASE_SPREADSHEET_ID`
   - **Save this ID**

### 1.3 Create the Matching Spreadsheet

This spreadsheet will contain one sheet (tab) per applicant showing their matches.

**Steps:**

1. Create a new Google Sheet
2. Name it something like "Housing Matches" or "Applicant Matching Sheets"
3. **Optionally create a TEMPLATE sheet:**
   - Right-click on "Sheet1" → Rename to "TEMPLATE"
   - Add any formulas or formatting you want in each applicant's matching sheet
   - If you don't create a template, the script will create blank sheets
4. **Get the Spreadsheet ID** from the URL
   - This is your `MATCHING_SPREADSHEET_ID`
   - **Save this ID**

### 1.4 Share Permissions

Make sure your Google account has **edit access** to all three spreadsheets. The Apps Script will need to write to them.

**To check:**
- Open each spreadsheet
- Click the **Share** button (top right)
- Ensure your account has "Editor" access

---

## Step 2: Apps Script Backend (Webhook)

The Apps Script acts as a webhook that receives data from JotForm and writes it to your Google Sheets.

### 2.1 Create a New Apps Script Project

1. Go to [script.google.com](https://script.google.com)
2. Click **New Project** (or the **+** button)
3. You'll see a blank code editor with a file called `Code.gs`

### 2.2 Paste the Webhook Code

1. Open the file `apps-script/webhook.gs` from this deliverable
2. **Copy the entire contents**
3. **Paste it into the Code.gs file** in Apps Script
4. **Replace the three spreadsheet IDs** at the top of the file:
   ```javascript
   const MASTER_SPREADSHEET_ID = 'YOUR_MASTER_SHEET_ID_HERE';
   const DATABASE_SPREADSHEET_ID = 'YOUR_INTAKE_SHEET_ID_HERE';
   const MATCHING_SPREADSHEET_ID = 'YOUR_MATCHING_SHEET_ID_HERE';
   ```
5. **Save the project** (Ctrl+S or Cmd+S)

### 2.3 Name Your Project

1. Click the project name at the top (it will say "Untitled project")
2. Rename it to something like "Accessible Housing Webhook"
3. Click **OK**

### 2.4 Deploy as Web App

This makes your script accessible via a URL that JotForm can call.

**Steps:**

1. Click **Deploy** → **New deployment** (or **Test deployments** if using the new IDE)
2. Click the **Select type** dropdown and choose **Web app**
3. Configure the deployment:
   - **Description**: "Housing Matcher Webhook v1" (or any description)
   - **Execute as**: **Me** (your account)
   - **Who has access**: **Anyone** (or "Anyone with Google account" - this allows JotForm to call it)
4. Click **Deploy**
5. **Authorize the script:**
   - You'll see a warning about needing authorization
   - Click **Authorize access**
   - Choose your Google account
   - Click **Advanced** → **Go to [Project Name] (unsafe)**
   - Click **Allow**
6. **Copy the Web App URL:**
   - After authorization, you'll see a "Web app" URL
   - It will look like: `https://script.google.com/macros/s/AKfycby.../exec`
   - **Copy this entire URL** - this is your webhook URL for JotForm
   - **Save this URL** - you'll need it in Step 3

### 2.5 Test the Webhook (Optional)

You can test if the webhook is working:

1. Copy your Web App URL
2. Open a new browser tab
3. Paste the URL and add `?test=1` at the end
4. You should see a JSON response like: `{"status":"error","message":"..."}`
   - This is expected - it means the webhook is accessible
   - The error is because we didn't send proper data

---

## Understanding the Apps Script Code

### What the Code Does

1. **`doPost(e)` function**: This is called by JotForm when a form is submitted
   - Receives JSON data from JotForm
   - Checks which "sheet" the data should go to (based on `data.sheet` field)
   - Writes the data to both the master sheet and intake sheet
   - If it's an applicant submission (`sheet === "Applicants"`), creates a matching sheet

2. **`appendToSpreadsheet()` function**: Writes a record to a specific sheet
   - Automatically creates the sheet if it doesn't exist
   - Adds missing column headers as needed
   - Appends the new row of data

3. **`createApplicantSheet()` function**: Creates a personalized matching sheet for each applicant
   - Uses the applicant's name and timestamp to create a unique sheet name
   - Writes the applicant's data
   - Sets up formulas to import data from master and intake sheets
   - Leaves a placeholder for matching formulas (you can customize this later)

### Important Notes

- **The `sheet` field**: JotForm needs to send a field called `sheet` with value `"Applicants"` or `"Units"` to route data correctly
- **IMPORTRANGE formulas**: When creating applicant sheets, the script uses `IMPORTRANGE()` to pull data from other sheets. The first time this runs, Google will ask for permission to access those sheets.
- **Error handling**: The script will log errors to the Apps Script execution log, but won't crash if something goes wrong

### Troubleshooting

**Problem: "Permission denied" errors**
- Make sure you've authorized the script (Step 2.4)
- Check that your account has edit access to all three spreadsheets

**Problem: Data not appearing in sheets**
- Check the Apps Script execution log: **Executions** (left sidebar) → View recent executions
- Look for error messages
- Make sure the spreadsheet IDs are correct (no extra spaces or quotes)

**Problem: Webhook URL not working**
- Make sure you deployed as "Web app" (not "API Executable")
- Check that "Who has access" is set to "Anyone" or "Anyone with Google account"
- Try redeploying and getting a new URL

---

## Next Steps

Once your Apps Script is deployed and you have the Web App URL, continue to **Part 3: JotForm & WordPress Integration**.

