# Automatic Render Deployment Setup

## 🎯 Goal: Automatically Deploy Backend to Render

Unfortunately, Render doesn't have a fully automated CLI setup that can create services without user interaction (for security reasons). However, I've set up everything to make it as easy as possible!

## ✅ What's Already Done:

1. ✅ **render.yaml configured** - Render will auto-detect this file
2. ✅ **All backend code in GitHub** - Ready for Render to deploy
3. ✅ **Deployment script created** - `deploy-to-render.sh`

## 🚀 Quickest Setup (5 minutes):

### Step 1: Go to Render Dashboard
Visit: https://dashboard.render.com

### Step 2: Connect GitHub & Create Service
1. Click **"New +"** → **"Web Service"**
2. **Connect GitHub** (if not already connected)
3. **Select repository:** `sainisomesh/accessible-housing-matcher`
4. Render will **automatically detect** `backend/render.yaml` ✅
5. Click **"Create Web Service"**

### Step 3: Add Environment Variables
In the Render dashboard, go to **Environment** tab and add:

- **APPS_SCRIPT_URL** = Your Google Apps Script Web App URL
- **CORS_ORIGINS** = `https://sainisomesh.github.io` (already set in render.yaml)
- **DATABASE_URL** = (leave empty for SQLite)

### Step 4: Get Your Backend URL
Once deployed, Render will give you a URL like:
`https://accessible-housing-backend.onrender.com`

### Step 5: Update Frontend Config
1. Edit `frontend/src/config.js` in GitHub
2. Update: `export const API_URL = 'https://your-actual-backend-url.onrender.com'`
3. Commit and push - GitHub Actions will auto-deploy

---

## 🔄 Auto-Deploy Setup (After Initial Creation)

Once your Render service is created, it will **automatically deploy** whenever you push to GitHub!

**How it works:**
- Render watches your GitHub repository
- Every push to `main` branch triggers a new deployment
- No manual steps needed after initial setup

---

## 📝 Alternative: Use Render CLI (Advanced)

If you want to use the CLI:

```bash
# Install Render CLI
npm install -g @render/cli

# Login to Render
render login

# Deploy (from project root)
render deploy
```

---

## ✅ Summary

**What you need to do manually (one time):**
1. Go to Render dashboard
2. Create Web Service from GitHub repo
3. Add environment variables
4. Get backend URL
5. Update frontend config

**After that:**
- ✅ Auto-deploys on every GitHub push
- ✅ No manual steps needed
- ✅ Everything connected automatically

---

## 🆘 Need Help?

See the detailed guide: **[Backend Render Setup](docs/BACKEND-RENDER-SETUP.md)**

The render.yaml file is already configured correctly - Render will use it automatically when you connect your GitHub repository!

