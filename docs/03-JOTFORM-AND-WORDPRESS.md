# Part 3: JotForm & WordPress Integration

## Step 3: JotForm Setup & Webhook Integration

JotForm will collect submissions from applicants and landlords, then send that data to your Apps Script webhook.

### 3.1 Create the Applicant Form

This form collects information from people looking for housing.

**Steps:**

1. Log in to [JotForm](https://www.jotform.com)
2. Click **Create Form** → **Start from Scratch** (or use a template)
3. **Add form fields** that match your needs. At minimum, include:
   - Name (Short Answer or Name field)
   - Annual Income (Number field)
   - Voucher Type (Dropdown: None, Section 8, Housing Choice Voucher, Other)
   - Location (Short Answer - City/ZIP)
   - Household Size (Number field)
   - Accessibility Needs (Checkboxes: Wheelchair Access, Elevator Access, Ramp Access, etc.)
   - Contact (Email field)

4. **Add a hidden field for routing:**
   - Add a **Hidden Field** to your form
   - Set the field name/label to: `sheet`
   - Set the default value to: `Applicants`
   - This tells the Apps Script which sheet to write to

5. **Save the form** and note the **Form ID** (visible in the form URL or settings)

### 3.2 Create the Landlord Form (Optional)

If landlords will submit properties via JotForm, create a second form.

**Steps:**

1. Create a new form in JotForm
2. **Add form fields** for property listings:
   - Property Name
   - Address
   - Rent (Number)
   - Accessibility Features (Checkboxes)
   - Contact Information
   - Availability Status
   - Photo URL (optional)

3. **Add a hidden field:**
   - Field name: `sheet`
   - Default value: `Units`
   - This routes landlord submissions to the "Units" sheet

4. **Save the form** and note the **Form ID**

### 3.3 Set Up the Webhook

Connect your JotForm to the Apps Script webhook.

**Steps:**

1. **Open your Applicant form** in JotForm
2. Go to **Settings** → **Integrations** (or **Workflow** → **Integrations**)
3. Find **Webhooks** and click **Add**
4. **Paste your Apps Script Web App URL** (from Step 2.4)
5. **Set the method to POST** (should be default)
6. **Save the webhook**
7. **Repeat for the Landlord form** (if you created one)

### 3.4 Test the Webhook Connection

**Steps:**

1. **Submit a test entry** in your JotForm
2. **Check your Google Sheets:**
   - Open your intake spreadsheet (`DATABASE_SPREADSHEET_ID`)
   - You should see a new row with the test data
   - Check your master spreadsheet - it should also have the data
3. **Check the Apps Script execution log:**
   - Go to script.google.com
   - Open your project
   - Click **Executions** (left sidebar)
   - You should see recent executions with "Success" status

**If data doesn't appear:**
- Check that the webhook URL is correct (no extra spaces)
- Verify the `sheet` hidden field is set correctly
- Check Apps Script execution log for errors
- Make sure the spreadsheet IDs in Apps Script are correct

---

## Step 4: Frontend UI & WordPress Integration

**⚠️ Important:** WordPress **cannot** host the frontend or backend. They must be hosted separately. See [WordPress Hosting Explanation](WORDPRESS-HOSTING-EXPLANATION.md) for details.

The frontend is a React-based search interface that users interact with to find housing matches.

### 4.1 Understanding the Frontend

The frontend code is in the `frontend/` folder. It includes:
- **React components** for the search form and match results
- **CSS styling** for a professional appearance
- **Configuration file** (`src/config.js`) where you set your API URL and form links

**How it works:**
- Users fill out a form with their housing needs
- The frontend calls your backend API (or reads from Google Sheets)
- Matches are calculated and displayed in real-time
- Users can save/bookmark matches they're interested in

### 4.2 Configure the Frontend

Before deploying, update the configuration:

1. **Open `frontend/src/config.js`**
2. **Update these values:**
   ```javascript
   // Your backend API URL (if using the Python/FastAPI backend)
   export const API_URL = 'https://your-backend-api.onrender.com'
   
   // Your JotForm URLs
   export const JOTFORM_APPLICANT_URL = 'https://form.jotform.com/YOUR_FORM_ID'
   export const JOTFORM_LANDLORD_URL = 'https://form.jotform.com/YOUR_FORM_ID'
   
   // Your logo URL (optional)
   export const LOGO_URL = 'https://your-website.com/logo.png'
   ```

3. **Save the file**

### 4.3 Build the Frontend

The frontend needs to be built (compiled) before it can be used.

**Option A: Using Node.js (Recommended)**

1. **Install Node.js** if you don't have it: [nodejs.org](https://nodejs.org)
2. **Open a terminal/command prompt**
3. **Navigate to the frontend folder:**
   ```bash
   cd accessible-housing-final-deliverable/frontend
   ```
4. **Install dependencies:**
   ```bash
   npm install
   ```
5. **Build the frontend:**
   ```bash
   npm run build
   ```
6. **The built files will be in the `dist/` folder**

**Option B: Use an Online Builder**

If you don't have Node.js, you can use online services like:
- [CodeSandbox](https://codesandbox.io) - Import the frontend folder and build there
- [StackBlitz](https://stackblitz.com) - Similar online IDE

### 4.4 Embedding in WordPress

**💰 Want FREE hosting?** See [Free Hosting Setup Guide](FREE-HOSTING-SETUP.md) for step-by-step instructions to host frontend on GitHub Pages (free) and backend on Render (free tier).

You have two main options for embedding the frontend in WordPress.

#### Option A: Embed as an iframe (Easiest)

**Steps:**

1. **Host the built frontend:**
   - Upload the `dist/` folder contents to a web hosting service
   - Options: GitHub Pages, Netlify, Vercel, or your own web server
   - Get the URL where it's hosted (e.g., `https://your-site.netlify.app`)

2. **In WordPress:**
   - Edit the page where you want the housing matcher
   - Add a **Custom HTML** block
   - Paste this code (replace with your URL):
     ```html
     <iframe 
       src="https://your-hosted-frontend-url.com" 
       width="100%" 
       height="1200" 
       frameborder="0"
       style="border: none; min-height: 1200px;">
     </iframe>
     ```
   - Adjust the `height` value as needed
   - **Publish** the page

#### Option B: Embed HTML/JS Directly (More Control)

**Steps:**

1. **Extract the built files:**
   - From the `dist/` folder, you'll need:
     - `index.html`
     - All files in the `assets/` folder

2. **Upload to WordPress:**
   - Use WordPress File Manager plugin, or
   - Upload via FTP to your WordPress theme folder, or
   - Use a custom HTML block with inline code

3. **Add to WordPress page:**
   - Edit your page
   - Add a **Custom HTML** block
   - Copy the contents of `index.html` and paste it
   - Update any asset paths to point to where you uploaded the files

**Note:** This option requires more technical knowledge. Option A (iframe) is recommended for most users.

### 4.5 WordPress Plugin Alternative

**Note:** The WordPress plugin does NOT host the frontend or backend. It's just a PHP shortcode that calls your backend API (which must be hosted separately on Render/Railway/etc.).

If you prefer a WordPress plugin approach:

1. **Copy the file** `wordpress/housing-matcher-shortcode.php`
2. **Upload it to your WordPress site:**
   - Go to **Plugins** → **Add New** → **Upload Plugin**
   - Upload the PHP file
   - **Activate** the plugin

3. **Configure the plugin:**
   - Edit the PHP file
   - Find the line: `'api_url' => 'https://your-api-domain.com'`
   - Replace with your backend API URL
   - Save the file

4. **Use shortcodes in WordPress:**
   - In any page or post, add: `[housing_units]` to display all units
   - Or: `[housing_matches applicant_id="123"]` to show matches for a specific applicant

---

## Step 5: Backend API (Optional)

**Note:** The system can work with just Google Sheets and Apps Script. However, if you want real-time matching and a more robust system, you can deploy the Python/FastAPI backend.

### 5.1 When to Use the Backend

Use the backend if you want:
- Real-time matching calculations
- More complex matching algorithms
- Better performance with large datasets
- API endpoints for the frontend to call

**Skip the backend if:**
- You're comfortable with Google Sheets formulas for matching
- You have a small number of housing units
- You want the simplest possible setup

### 5.2 Deploying the Backend (If Needed)

The backend code is in the `backend/` folder. To deploy:

1. **Choose a hosting service:**
   - **Render** (recommended - free tier available): [render.com](https://render.com)
   - **Railway**: [railway.app](https://railway.app)
   - **Heroku**: [heroku.com](https://heroku.com)

2. **Follow the hosting service's instructions** to:
   - Connect your GitHub repository (or upload the backend folder)
   - Set environment variables (like `APPS_SCRIPT_DEPLOY_URL`)
   - Deploy the application

3. **Get your backend URL** (e.g., `https://your-api.onrender.com`)

4. **Update the frontend config:**
   - In `frontend/src/config.js`, set `API_URL` to your backend URL

---

## Step 6: How to Reconfigure for Your Own Environment

Here's a checklist of all the places you need to update IDs and URLs:

### Configuration Checklist

- [ ] **Apps Script** (`apps-script/webhook.gs`):
  - [ ] `MASTER_SPREADSHEET_ID` - Your master housing sheet ID
  - [ ] `DATABASE_SPREADSHEET_ID` - Your JotForm intake sheet ID
  - [ ] `MATCHING_SPREADSHEET_ID` - Your matching spreadsheet ID

- [ ] **JotForm Webhook Settings**:
  - [ ] Applicant form webhook URL → Your Apps Script Web App URL
  - [ ] Landlord form webhook URL → Your Apps Script Web App URL

- [ ] **Frontend Config** (`frontend/src/config.js`):
  - [ ] `API_URL` - Your backend API URL (or leave as localhost for development)
  - [ ] `JOTFORM_APPLICANT_URL` - Your applicant form URL
  - [ ] `JOTFORM_LANDLORD_URL` - Your landlord form URL
  - [ ] `LOGO_URL` - Your organization's logo URL (optional)

- [ ] **WordPress Plugin** (if using):
  - [ ] `api_url` in `housing-matcher-shortcode.php` → Your backend API URL

### Sanity Check Workflow

Test that everything is connected:

1. **Submit a test entry in JotForm:**
   - Fill out the applicant form with test data
   - Submit it

2. **Check Google Sheets:**
   - Open your intake spreadsheet
   - You should see a new row with your test data
   - Check your master spreadsheet - it should also have the data

3. **Check Matching Spreadsheet:**
   - Open your matching spreadsheet
   - You should see a new sheet (tab) with the applicant's name and timestamp
   - The sheet should contain the applicant's data and imported housing data

4. **Test the Frontend:**
   - Open your WordPress page with the embedded frontend
   - Fill out the search form
   - You should see matching results appear

5. **Check for Errors:**
   - Open browser console (F12) to see any JavaScript errors
   - Check Apps Script execution log for any errors
   - Verify all URLs and IDs are correct

---

## Troubleshooting Common Issues

### Issue: JotForm submissions not appearing in sheets

**Solutions:**
- Verify the webhook URL is correct (no extra spaces, includes `/exec` at the end)
- Check that the `sheet` hidden field is set correctly in JotForm
- Look at Apps Script execution log for error messages
- Make sure spreadsheet IDs in Apps Script are correct

### Issue: Frontend not loading matches

**Solutions:**
- Check browser console (F12) for errors
- Verify `API_URL` in `config.js` is correct
- Make sure your backend is running (if using backend)
- Check CORS settings if getting "blocked by CORS" errors

### Issue: IMPORTRANGE not working in matching sheets

**Solutions:**
- The first time IMPORTRANGE runs, Google will ask for permission
- Click "Allow access" when prompted
- If it still doesn't work, manually grant access:
  - In the matching spreadsheet, click the cell with the IMPORTRANGE formula
  - You should see a permission prompt - click "Allow"

### Issue: Frontend shows "Failed to load units"

**Solutions:**
- Check that your backend API is running and accessible
- Verify the API URL in `config.js` matches your actual backend URL
- Test the API directly: Open `https://your-api-url.com/units` in a browser
- Check CORS settings on your backend

---

## Next Steps

Once everything is configured and tested:

1. **Populate your master housing sheet** with real housing data
2. **Customize the matching formulas** in the matching spreadsheet (if needed)
3. **Style the frontend** to match your website's design (edit `App.css`)
4. **Test with real users** and gather feedback

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the Apps Script execution log
3. Check browser console for frontend errors
4. Verify all IDs and URLs are correct

Good luck with your implementation!

