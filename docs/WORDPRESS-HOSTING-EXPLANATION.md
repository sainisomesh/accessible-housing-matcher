# WordPress Hosting Explanation

## ⚠️ Important: WordPress Cannot Host the Frontend or Backend

**WordPress does NOT host the frontend or backend.** Here's what actually needs to be hosted where:

## What Needs to Be Hosted Where

### 1. **Backend API (Python/FastAPI)** - Must be hosted separately
- **Cannot run on WordPress** - WordPress is PHP-based, the backend is Python
- **Hosting options:**
  - Render.com (recommended - free tier)
  - Railway.app
  - Heroku
  - Any Python hosting service
- **What it does:** Provides API endpoints (`/units`, `/applicants`, `/match/{id}`, etc.)
- **Example URL:** `https://your-api.onrender.com`

### 2. **Frontend (React App)** - Must be hosted separately
- **Cannot run on WordPress** - WordPress doesn't run Node.js/React apps
- **Hosting options:**
  - Netlify (recommended - free tier)
  - Vercel
  - GitHub Pages
  - Any static hosting service
- **What it does:** The interactive search interface users see
- **Example URL:** `https://your-frontend.netlify.app`

### 3. **WordPress Plugin** - Runs on WordPress (but doesn't host anything)
- **What it is:** A PHP shortcode plugin that makes API calls to your backend
- **What it does:** Displays housing units/matches by calling your backend API
- **What it does NOT do:** Host the frontend or backend

## How It All Works Together

### Option 1: Full React Frontend (Recommended)

```
User visits WordPress page
    ↓
WordPress page contains an iframe
    ↓
iframe loads the React frontend (hosted on Netlify/Vercel)
    ↓
React frontend makes API calls to backend (hosted on Render/Railway)
    ↓
Backend returns data
    ↓
React frontend displays results to user
```

**Setup:**
1. Build the React frontend (`npm run build`)
2. Host the `dist/` folder on Netlify/Vercel
3. Host the backend on Render/Railway
4. Embed the frontend URL in WordPress as an iframe

### Option 2: WordPress Plugin with Shortcodes

```
User visits WordPress page
    ↓
WordPress page contains shortcode: [housing_units]
    ↓
WordPress plugin (PHP) makes API call to backend
    ↓
Backend returns data
    ↓
WordPress plugin displays results as HTML
```

**Setup:**
1. Upload the PHP plugin to WordPress
2. Configure the plugin with your backend API URL
3. Use shortcodes in WordPress pages: `[housing_units]` or `[housing_matches applicant_id="123"]`
4. Host the backend on Render/Railway

## What the WordPress Plugin Actually Does

The WordPress plugin (`housing-matcher-shortcode.php`) is **NOT** hosting anything. It's just a PHP script that:

1. **Receives shortcode calls** from WordPress pages (e.g., `[housing_units]`)
2. **Makes HTTP requests** to your backend API (hosted elsewhere)
3. **Formats the response** as HTML
4. **Displays it** on the WordPress page

Think of it like a "middleman" - it connects WordPress to your backend API.

## Summary

| Component | Can WordPress Host It? | Where to Host |
|-----------|------------------------|---------------|
| **Backend API** | ❌ No (Python, not PHP) | Render, Railway, Heroku |
| **Frontend (React)** | ❌ No (Node.js/React, not PHP) | Netlify, Vercel, GitHub Pages |
| **WordPress Plugin** | ✅ Yes (it's PHP) | WordPress plugins folder |

## Quick Setup Checklist

- [ ] Deploy backend to Render/Railway → Get backend URL
- [ ] Build frontend (`npm run build`)
- [ ] Deploy frontend to Netlify/Vercel → Get frontend URL
- [ ] In WordPress: Either embed frontend as iframe OR use plugin shortcodes
- [ ] Configure plugin with backend URL (if using plugin option)

## Why This Architecture?

- **WordPress limitations:** WordPress runs PHP and MySQL, not Python or Node.js
- **Best practices:** Separating frontend, backend, and CMS is standard practice
- **Scalability:** Each component can scale independently
- **Flexibility:** You can update frontend/backend without touching WordPress

## Need Help?

If you're confused about hosting:
1. Use **Cursor AI** or **ChatGPT** to help you deploy to Render (backend) and Netlify (frontend)
2. Follow the step-by-step guides in the documentation
3. The hosting services have their own tutorials for deployment

