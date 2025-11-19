# GitHub Pages Quick Start

## ✅ Everything is Ready!

Your frontend is already built and ready to deploy to GitHub Pages. Here's how to complete the setup:

---

## Option 1: Automatic Deployment (Recommended)

### Step 1: Create GitHub Repository

1. Go to [github.com](https://github.com) and sign in
2. Click **"New repository"** (green button)
3. Name it: `accessible-housing-matcher` (or your choice)
4. Make it **Public** (required for free GitHub Pages)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

### Step 2: Push Your Code

Run these commands in your terminal:

```bash
cd /Users/somesh/Desktop/accessible-housing-final-deliverable

# If you haven't committed yet:
git commit -m "Initial commit: Accessible Housing Matcher with GitHub Pages"

# Add your GitHub repository (replace with your actual repo URL):
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub:
git branch -M main
git push -u origin main
```

**Or use the provided script:**
```bash
./deploy-to-github-pages.sh https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under **"Source"**, select **"GitHub Actions"**
5. Click **Save**

### Step 4: Wait for Deployment

1. Go to the **Actions** tab in your repository
2. You'll see a workflow running called "Deploy to GitHub Pages"
3. Wait 2-3 minutes for it to complete
4. When it's done, you'll see a green checkmark ✅

### Step 5: Get Your Frontend URL

Your frontend will be live at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME
```

**Example:**
- Username: `johndoe`
- Repo: `accessible-housing-matcher`
- URL: `https://johndoe.github.io/accessible-housing-matcher`

---

## Option 2: Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Build the frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Create gh-pages branch:**
   ```bash
   cd dist
   git init
   git add .
   git commit -m "Deploy to GitHub Pages"
   git branch -M gh-pages
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin gh-pages
   ```

3. **Enable GitHub Pages:**
   - Go to repository **Settings** → **Pages**
   - Source: **Deploy from a branch**
   - Branch: `gh-pages`
   - Folder: `/ (root)`
   - Click **Save**

---

## Next Steps

Once your frontend is deployed:

1. ✅ **Get your GitHub Pages URL** (format: `https://username.github.io/repo-name`)
2. ✅ **Deploy backend to Render** - See [Backend Render Setup Guide](docs/BACKEND-RENDER-SETUP.md)
3. ✅ **Update frontend config** - Edit `frontend/src/config.js` with your Render backend URL
4. ✅ **Embed in WordPress** - Use iframe to embed your GitHub Pages site

---

## Troubleshooting

**Problem: GitHub Actions workflow not running**
- **Solution:** Make sure you selected "GitHub Actions" as the source in Pages settings
- **Check:** Go to Actions tab - you should see the workflow

**Problem: 404 error on GitHub Pages**
- **Solution:** Wait a few minutes for changes to propagate
- **Check:** Make sure the workflow completed successfully (green checkmark)

**Problem: Assets not loading (CSS/JS broken)**
- **Solution:** Check `frontend/vite.config.js` - update `base` path if needed
- **Example:** If repo is `accessible-housing-matcher`, set: `base: '/accessible-housing-matcher/'`

---

## Need Help?

If you get stuck:
1. Check the [Free Hosting Setup Guide](docs/FREE-HOSTING-SETUP.md) for detailed instructions
2. Use Cursor AI or ChatGPT to help guide you
3. Check GitHub Actions logs in the Actions tab

Good luck! 🚀

