# Backend Deployment to Render.com (FREE)

## 🎯 Quick Overview

This guide shows you how to deploy the **backend API to Render.com** (free tier). The frontend is already set up on GitHub Pages and will connect to this backend.

**What you'll get:**
- Free backend hosting on Render.com
- Automatic HTTPS
- Easy deployment from GitHub
- 750 hours/month (free tier)

**Time required:** 15-20 minutes

---

## Prerequisites

Before starting, make sure you have:
- ✅ Your frontend already deployed on GitHub Pages (or ready to deploy)
- ✅ Your GitHub repository URL
- ✅ Your Google Apps Script Web App URL (from Part 2 of the main setup)
- ✅ A Render.com account (free)

---

## Step 1: Create Render Account

1. **Go to [render.com](https://render.com)**
2. **Click "Get Started for Free"**
3. **Sign up** with GitHub (recommended - makes deployment easier) or email
4. **Verify your email** if required

---

## Step 2: Prepare Your Backend Code on GitHub

Your backend code needs to be in a GitHub repository. If it's not already:

1. **Create a GitHub repository** (if you don't have one):
   - Go to [github.com](https://github.com)
   - Click **New repository**
   - Name it (e.g., `accessible-housing-matcher`)
   - Make it **Public** (free tier on Render requires public repos, or connect via Git)
   - Click **Create repository**

2. **Push your code to GitHub:**
   ```bash
   cd /path/to/accessible-housing-final-deliverable
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   
   Or use the provided script:
   ```bash
   ./deploy-to-github-pages.sh https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

---

## Step 3: Create Web Service on Render

1. **In Render dashboard, click "New +" → "Web Service"**

2. **Connect your repository:**
   - If you signed up with GitHub, you'll see your repositories listed
   - **Select your repository** that contains the backend code
   - Or click "Public Git repository" and paste your GitHub repo URL
   - Click **Connect**

3. **Configure the service:**
   
   **Basic Settings:**
   - **Name:** `accessible-housing-backend` (or your choice)
   - **Region:** Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch:** `main` (or `master` if that's your default)
   - **Root Directory:** `backend` ⚠️ **IMPORTANT** - This tells Render where your backend code is
   
   **Build & Deploy:**
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   
   **Plan:**
   - Select **Free** (if available)
   - Note: Free tier spins down after 15 minutes of inactivity (first request may take 30-60 seconds)

4. **Click "Create Web Service"**

---

## Step 4: Configure Environment Variables

1. **In your Render service dashboard, go to "Environment" tab**

2. **Add these environment variables** (click "Add Environment Variable" for each):

   **Variable 1: APPS_SCRIPT_URL**
   - **Key:** `APPS_SCRIPT_URL`
   - **Value:** Your Google Apps Script Web App URL
   - Example: `https://script.google.com/macros/s/AKfycbz.../exec`
   - ⚠️ **Get this from Part 2 of the main setup guide**

   **Variable 2: CORS_ORIGINS**
   - **Key:** `CORS_ORIGINS`
   - **Value:** Your GitHub Pages frontend URL
   - Format: `https://YOUR_USERNAME.github.io/REPO_NAME`
   - Or if using custom domain: `https://yourdomain.com`
   - ⚠️ **If you don't have the frontend URL yet, use `*` temporarily (update later)**

   **Variable 3: DATABASE_URL (Optional)**
   - **Key:** `DATABASE_URL`
   - **Value:** Leave empty (uses SQLite by default)
   - Or add PostgreSQL connection string if you set up a database

3. **Click "Save Changes"**

   Render will automatically redeploy when you save environment variables.

---

## Step 5: Wait for Deployment

1. **Watch the deployment logs:**
   - You'll see build logs in the dashboard
   - First deployment takes 5-10 minutes
   - Look for "Your service is live" message

2. **Check deployment status:**
   - Status should show **"Live"** (green)
   - If there are errors, check the logs tab

---

## Step 6: Get Your Backend URL

1. **Once deployment is complete, copy your backend URL:**
   - It will be at the top of your service dashboard
   - Format: `https://accessible-housing-backend.onrender.com`
   - Or: `https://your-service-name.onrender.com`

2. **Test your backend:**
   - Open the URL in your browser
   - You should see: `{"message":"HousingMatcher API is running"}`
   - Try: `https://your-backend-url.onrender.com/docs` for API documentation

3. **Save this URL** - you'll need it for the frontend!

---

## Step 7: Update Frontend Configuration

Now that your backend is live, update your frontend to use it:

1. **If frontend is on GitHub Pages:**
   - Edit `frontend/src/config.js` in your repository
   - Update the API URL:
     ```javascript
     export const API_URL = 'https://your-backend-url.onrender.com'
     ```
   - Commit and push the changes
   - GitHub Actions will automatically rebuild and redeploy

2. **If frontend is local:**
   - Edit `frontend/src/config.js`
   - Update: `export const API_URL = 'https://your-backend-url.onrender.com'`
   - Rebuild: `npm run build`

---

## Step 8: Update CORS (If Needed)

If you didn't set the correct CORS_ORIGINS earlier:

1. **Go to Render dashboard** → Your backend service → **Environment** tab
2. **Update `CORS_ORIGINS`:**
   - **Value:** Your actual GitHub Pages URL
   - Example: `https://yourusername.github.io/accessible-housing-matcher`
3. **Save** - Render will automatically redeploy

---

## Step 9: Test Everything

1. **Test backend directly:**
   - Visit: `https://your-backend-url.onrender.com`
   - Should see: `{"message":"HousingMatcher API is running"}`
   - Visit: `https://your-backend-url.onrender.com/units`
   - Should see JSON array (may be empty if no units yet)

2. **Test frontend connection:**
   - Open your GitHub Pages frontend
   - Open browser console (F12)
   - Fill out the form
   - Check for any errors
   - Matches should appear (or empty state if no units)

3. **Test WordPress integration:**
   - Visit your WordPress page with the embedded frontend
   - Test the form submission
   - Verify matches are displayed

---

## Troubleshooting

### Backend Issues

**Problem: "Service unavailable" or timeout**
- **Cause:** Free tier spins down after 15 minutes of inactivity
- **Solution:** First request after spin-down takes 30-60 seconds (this is normal)
- **Upgrade:** Consider paid tier ($7/month) for always-on service

**Problem: Build fails**
- **Check:** Build logs in Render dashboard
- **Common issues:**
  - Missing `requirements.txt` → Make sure it exists in `backend/` folder
  - Wrong root directory → Should be `backend` (not root)
  - Python version → Render uses Python 3 by default

**Problem: CORS errors in browser**
- **Check:** `CORS_ORIGINS` environment variable includes your frontend URL
- **Fix:** Update `CORS_ORIGINS` in Render dashboard → Environment tab
- **Wait:** Allow a few minutes for changes to deploy

**Problem: Environment variables not working**
- **Check:** Variable names are exact (case-sensitive: `APPS_SCRIPT_URL` not `apps_script_url`)
- **Check:** No extra spaces in values
- **Fix:** Delete and re-add the variable

**Problem: "Module not found" errors**
- **Check:** `requirements.txt` includes all dependencies
- **Fix:** Make sure `requirements.txt` is in the `backend/` folder
- **Check:** Build command is: `pip install -r requirements.txt`

### Connection Issues

**Problem: Frontend can't connect to backend**
- **Check:** Backend URL in `frontend/src/config.js` is correct
- **Check:** Backend is live (visit the URL directly)
- **Check:** CORS_ORIGINS includes your frontend URL
- **Check:** Browser console (F12) for specific error messages

**Problem: "Failed to fetch" errors**
- **Check:** Backend URL includes `https://` (not `http://`)
- **Check:** No typos in the URL
- **Check:** Backend service is not sleeping (free tier limitation)

---

## Free Tier Limitations

**Render Free Tier:**
- ✅ 750 hours/month (enough for 24/7)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes 30-60 seconds
- ✅ Automatic HTTPS
- ✅ Easy deployment from GitHub

**If you need always-on service:**
- Upgrade to **Starter** plan ($7/month)
- No spin-down
- Faster response times

---

## Next Steps

Once your backend is deployed:

1. ✅ **Test all endpoints** using `/docs` interface
2. ✅ **Sync data from Google Sheets** (if needed)
3. ✅ **Update frontend config** with backend URL
4. ✅ **Test complete flow** (form → matching → results)
5. ✅ **Embed in WordPress** (see WordPress integration guide)

---

## Quick Reference

**Backend URL format:**
```
https://your-service-name.onrender.com
```

**Environment Variables needed:**
- `APPS_SCRIPT_URL` - Your Google Apps Script Web App URL
- `CORS_ORIGINS` - Your frontend URL (GitHub Pages)
- `DATABASE_URL` - (Optional, leave empty for SQLite)

**Important Settings:**
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## Need Help?

If you get stuck:
1. **Check Render logs** - Go to your service → Logs tab
2. **Check browser console** - F12 → Console tab for frontend errors
3. **Use Cursor AI or ChatGPT** - Describe your issue and it can help guide you
4. **Review the main setup guide** - Make sure you completed all prerequisites

Good luck! 🚀

