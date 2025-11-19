# Free Hosting Setup Guide

## 🎯 Overview

This guide shows you how to host everything for **FREE**:
- **Frontend:** GitHub Pages (completely free) - ✅ **Already set up!**
- **Backend:** Render.com (free tier available)
- **WordPress:** Connect to your GitHub Pages site

**Total Cost: $0** ✅

**📝 Note:** The frontend is already configured for GitHub Pages deployment. If you need to deploy the frontend, see the GitHub Pages section below. Otherwise, jump to **Part 1** for backend deployment.

---

## Quick Start: Frontend Already on GitHub Pages?

If your frontend is already deployed on GitHub Pages, skip to:
👉 **[Backend Deployment to Render](BACKEND-RENDER-SETUP.md)** - Simplified guide focusing just on backend

---

## Part 1: Deploy Backend to Render.com (FREE)

Render.com offers a free tier that's perfect for this project. The free tier includes:
- 750 hours/month (enough for 24/7 operation)
- Automatic HTTPS
- Easy deployment from GitHub

### Step 1.1: Create Render Account

1. **Go to [render.com](https://render.com)**
2. **Click "Get Started for Free"**
3. **Sign up** with GitHub (recommended) or email
4. **Verify your email** if required

### Step 1.2: Prepare Your Backend Code

1. **Make sure your backend code is on GitHub:**
   - If you haven't already, create a GitHub repository
   - Upload your entire project (including the `backend/` folder)
   - Or use GitHub Desktop/Git to push your code

2. **Check your backend structure:**
   ```
   backend/
   ├── main.py
   ├── models.py
   ├── database.py
   ├── utils.py
   ├── requirements.txt
   └── __init__.py
   ```

### Step 1.3: Create New Web Service on Render

1. **In Render dashboard, click "New +" → "Web Service"**

2. **Connect your repository:**
   - If you signed up with GitHub, select your repository
   - Or click "Public Git repository" and paste your GitHub repo URL
   - Click "Connect"

3. **Configure the service:**
   - **Name:** `accessible-housing-backend` (or your choice)
   - **Region:** Choose closest to you (e.g., `Oregon (US West)`)
   - **Branch:** `main` (or `master` if that's your default branch)
   - **Root Directory:** `backend` ⚠️ **IMPORTANT** - This tells Render where your backend code is
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Select **Free** (if available, otherwise Starter is fine)

4. **Click "Create Web Service"**

### Step 1.4: Configure Environment Variables

1. **In your Render service dashboard, go to "Environment" tab**

2. **Add these environment variables:**
   - Click "Add Environment Variable" for each:
   
   **Variable 1:**
   - **Key:** `APPS_SCRIPT_URL`
   - **Value:** Your Google Apps Script Web App URL (from Part 2)
   - Example: `https://script.google.com/macros/s/AKfycbz.../exec`
   
   **Variable 2:**
   - **Key:** `CORS_ORIGINS`
   - **Value:** Your GitHub Pages URL (we'll get this in Part 2)
   - For now, use: `https://yourusername.github.io` (replace with your GitHub username)
   - Or use: `*` temporarily (we'll update this after frontend is deployed)
   
   **Variable 3 (Optional):**
   - **Key:** `DATABASE_URL`
   - **Value:** Leave empty (uses SQLite by default)
   - Or add PostgreSQL URL if you set up a database

3. **Click "Save Changes"**

### Step 1.5: Deploy and Get Your Backend URL

1. **Render will automatically start deploying**
   - You'll see build logs in the dashboard
   - First deployment takes 5-10 minutes
   - Subsequent deployments are faster

2. **Wait for deployment to complete:**
   - Look for "Your service is live" message
   - Status should show "Live"

3. **Copy your backend URL:**
   - It will be something like: `https://accessible-housing-backend.onrender.com`
   - **Save this URL** - you'll need it for the frontend!

4. **Test your backend:**
   - Open the URL in your browser
   - You should see: `{"message":"HousingMatcher API is running"}`
   - Try: `https://your-backend-url.onrender.com/docs` for API documentation

### Step 1.6: Update CORS After Frontend is Deployed

Once you have your GitHub Pages URL (from Part 2), come back and update:
- **Environment Variable:** `CORS_ORIGINS`
- **Value:** `https://yourusername.github.io` (your actual GitHub Pages URL)

---

## Part 2: Deploy Frontend to GitHub Pages (FREE)

GitHub Pages is completely free and perfect for hosting static React apps.

### Step 2.1: Prepare Your Frontend Code

1. **Update frontend configuration:**
   - Open `frontend/src/config.js`
   - Update the API URL:
     ```javascript
     export const API_URL = 'https://your-backend-url.onrender.com'
     ```
   - Replace with your actual Render backend URL from Part 1
   - Update JotForm URLs if needed
   - Save the file

2. **Build the frontend locally:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```
   - This creates a `dist/` folder with built files

### Step 2.2: Set Up GitHub Pages

**Option A: Using GitHub Actions (Recommended - Automatic)**

1. **Create GitHub Actions workflow:**
   - In your repository root, create folder: `.github/workflows/`
   - Create file: `.github/workflows/deploy.yml`
   - Paste this content:
   ```yaml
   name: Deploy to GitHub Pages
   
   on:
     push:
       branches: [ main ]
     workflow_dispatch:
   
   permissions:
     contents: read
     pages: write
     id-token: write
   
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Setup Node.js
           uses: actions/setup-node@v4
           with:
             node-version: '18'
             cache: 'npm'
             cache-dependency-path: frontend/package-lock.json
         
         - name: Install dependencies
           working-directory: ./frontend
           run: npm ci
         
         - name: Build
           working-directory: ./frontend
           run: npm run build
           env:
             VITE_API_URL: ${{ secrets.VITE_API_URL || 'https://your-backend-url.onrender.com' }}
         
         - name: Setup Pages
           uses: actions/configure-pages@v4
         
         - name: Upload artifact
           uses: actions/upload-pages-artifact@v3
           with:
             path: './frontend/dist'
     
     deploy:
       needs: build
       runs-on: ubuntu-latest
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v4
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click **Settings** → **Pages**
   - Under "Source", select **GitHub Actions**
   - Save

3. **Push your code:**
   ```bash
   git add .
   git commit -m "Add GitHub Pages deployment"
   git push
   ```

4. **Wait for deployment:**
   - Go to **Actions** tab in your repository
   - Watch the workflow run
   - When complete, your site will be at: `https://yourusername.github.io/repository-name`

**Option B: Manual Deployment (Simpler but Manual)**

1. **Build the frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create `gh-pages` branch:**
   ```bash
   cd frontend/dist
   git init
   git add .
   git commit -m "Deploy to GitHub Pages"
   git branch -M gh-pages
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin gh-pages
   ```

3. **Enable GitHub Pages:**
   - Go to repository **Settings** → **Pages**
   - Under "Source", select **Deploy from a branch**
   - Branch: `gh-pages`
   - Folder: `/ (root)`
   - Click **Save**

4. **Your site will be at:** `https://yourusername.github.io/repository-name`

### Step 2.3: Fix Base Path (If Needed)

If your repository name is not the root (e.g., `accessible-housing-final-deliverable`), you may need to update the base path:

1. **Check your `vite.config.js` or create it:**
   ```javascript
   import { defineConfig } from 'vite'
   import react from '@vitejs/plugin-react'
   
   export default defineConfig({
     plugins: [react()],
     base: '/repository-name/' // Replace with your actual repo name
   })
   ```

2. **Rebuild and redeploy**

### Step 2.4: Test Your Frontend

1. **Visit your GitHub Pages URL**
2. **Open browser console (F12)** to check for errors
3. **Test the form** - it should connect to your Render backend

---

## Part 3: Connect WordPress to GitHub Pages

Now that your frontend is hosted on GitHub Pages, you can embed it in WordPress.

### Step 3.1: Get Your GitHub Pages URL

Your frontend URL will be:
- `https://yourusername.github.io/repository-name`
- Or if using a custom domain: `https://yourdomain.com`

**Save this URL!**

### Step 3.2: Embed in WordPress (Easiest Method)

1. **In WordPress, edit the page** where you want the housing matcher

2. **Add a Custom HTML block:**
   - Click **+** to add block
   - Search for "Custom HTML"
   - Add the block

3. **Paste this code:**
   ```html
   <iframe 
     src="https://yourusername.github.io/repository-name" 
     width="100%" 
     height="1200" 
     frameborder="0"
     style="border: none; min-height: 1200px; width: 100%;">
   </iframe>
   ```
   - Replace `https://yourusername.github.io/repository-name` with your actual GitHub Pages URL
   - Adjust `height` as needed (1200px is a good starting point)

4. **Publish the page**

5. **Test it:**
   - Visit your WordPress page
   - The housing matcher should load in the iframe
   - Test the form to make sure it connects to your backend

### Step 3.3: Alternative - Link to GitHub Pages

Instead of embedding, you can link directly:

1. **In WordPress, add a button or link:**
   ```html
   <a href="https://yourusername.github.io/repository-name" 
      target="_blank" 
      class="button">
     Find Accessible Housing
   </a>
   ```

2. **This opens the housing matcher in a new tab**

### Step 3.4: Update Backend CORS

Now that you have your GitHub Pages URL, update your Render backend:

1. **Go to Render dashboard** → Your backend service → **Environment** tab

2. **Update `CORS_ORIGINS`:**
   - **Value:** `https://yourusername.github.io`
   - Or add multiple: `https://yourusername.github.io,https://your-wordpress-site.com`

3. **Save changes** - Render will automatically redeploy

---

## Part 4: Final Configuration Checklist

Before going live, verify:

- [ ] Backend is deployed on Render and accessible
- [ ] Backend URL works: `https://your-backend.onrender.com`
- [ ] Frontend `config.js` has correct backend URL
- [ ] Frontend is deployed on GitHub Pages
- [ ] Frontend URL works: `https://yourusername.github.io/repo-name`
- [ ] Backend CORS includes your GitHub Pages URL
- [ ] WordPress page embeds or links to GitHub Pages
- [ ] Test form submission works end-to-end
- [ ] Test matching functionality works

---

## Troubleshooting

### Backend Issues

**Problem: "Service unavailable" or timeout**
- **Solution:** Free tier on Render spins down after 15 minutes of inactivity
- First request after spin-down takes 30-60 seconds
- Consider upgrading to paid tier for always-on service

**Problem: CORS errors**
- **Solution:** Make sure `CORS_ORIGINS` in Render includes your GitHub Pages URL
- Check for typos in the URL
- Allow a few minutes for changes to deploy

**Problem: Environment variables not working**
- **Solution:** Make sure variable names are exact (case-sensitive)
- Redeploy after adding/changing variables

### Frontend Issues

**Problem: "Failed to fetch" or API errors**
- **Solution:** Check `API_URL` in `frontend/src/config.js`
- Make sure backend URL is correct (include `https://`)
- Check browser console (F12) for specific errors

**Problem: GitHub Pages shows 404**
- **Solution:** Make sure you deployed the `dist/` folder contents
- Check that GitHub Pages is enabled in repository settings
- Wait a few minutes for changes to propagate

**Problem: Assets not loading (CSS/JS broken)**
- **Solution:** Check base path in `vite.config.js`
- Make sure it matches your repository name
- Rebuild and redeploy

### WordPress Issues

**Problem: Iframe not showing**
- **Solution:** Some WordPress themes block iframes
- Try a different block type or contact your WordPress admin
- Consider using the link method instead

**Problem: Iframe too small/large**
- **Solution:** Adjust `height` in the iframe code
- Use `min-height` CSS for responsive sizing

---

## Cost Summary

| Service | Cost | What You Get |
|---------|------|--------------|
| **GitHub Pages** | **FREE** | Unlimited hosting for static sites |
| **Render.com** | **FREE** | 750 hours/month, auto HTTPS |
| **WordPress** | Your existing hosting | Just embeds the GitHub Pages site |
| **Total** | **$0/month** | Complete hosting solution! |

---

## Next Steps

1. **Test everything thoroughly** before going live
2. **Monitor Render dashboard** for any errors
3. **Set up monitoring** (optional but recommended)
4. **Consider upgrading Render** if you need always-on service (no spin-down)

---

## Need Help?

If you get stuck:
1. **Use Cursor AI or ChatGPT** - describe your issue and it can help guide you
2. **Check Render logs** - Go to your service → Logs tab
3. **Check GitHub Actions logs** - Go to Actions tab in your repository
4. **Check browser console** - F12 → Console tab for frontend errors

Good luck with your deployment! 🚀

