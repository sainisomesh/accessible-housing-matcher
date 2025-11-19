# Render Environment Variables Setup

## 🔧 How to Fill Out Environment Variables in Render

### Environment Variable: `APPS_SCRIPT_URL`

**Value to enter:**
```
https://script.google.com/macros/s/AKfycbyV8pw9XZ3fiUxw1Ko1iB9AYWkna1bFR2eqnmenGLt7R8ODvPHBe2CL5UQ4BdiCYTE/exec
```

**Steps in Render Dashboard:**
1. Go to your Render service dashboard
2. Click on **"Environment"** tab (left sidebar)
3. Under **"Environment Variables"**, click **"Add Environment Variable"**
4. **Key:** `APPS_SCRIPT_URL`
5. **Value:** Paste the URL above
6. Click **"Save Changes"**

---

### Environment Variable: `CORS_ORIGINS`

**Value to enter:**
```
https://sainisomesh.github.io
```

**Steps:**
1. Click **"Add Environment Variable"** again
2. **Key:** `CORS_ORIGINS`
3. **Value:** `https://sainisomesh.github.io`
4. Click **"Save Changes"**

---

### Environment Variable: `DATABASE_URL` (Optional)

**Value to enter:**
```
(Leave empty for SQLite, or add PostgreSQL connection string if you set up a database)
```

**Steps:**
- You can skip this one - it will use SQLite by default if left empty

---

## ✅ Complete Setup

After adding the environment variables:

1. **APPS_SCRIPT_URL** = `https://script.google.com/macros/s/AKfycbyV8pw9XZ3fiUxw1Ko1iB9AYWkna1bFR2eqnmenGLt7R8ODvPHBe2CL5UQ4BdiCYTE/exec`
2. **CORS_ORIGINS** = `https://sainisomesh.github.io`
3. **DATABASE_URL** = (leave empty)

Render will automatically redeploy when you save the environment variables.

---

## 🔍 Where to Find Your Apps Script URL (If Different)

If you need to find or update your Apps Script URL:

1. Go to [script.google.com](https://script.google.com)
2. Open your Apps Script project
3. Click **"Deploy"** → **"Manage deployments"**
4. Click the **"⚙️"** (settings) icon next to your deployment
5. Copy the **"Web app URL"**
6. It should look like: `https://script.google.com/macros/s/AKfycby.../exec`

---

## 📝 Quick Copy-Paste

**For APPS_SCRIPT_URL:**
```
https://script.google.com/macros/s/AKfycbyV8pw9XZ3fiUxw1Ko1iB9AYWkna1bFR2eqnmenGLt7R8ODvPHBe2CL5UQ4BdiCYTE/exec
```

**For CORS_ORIGINS:**
```
https://sainisomesh.github.io
```

That's it! 🎉

