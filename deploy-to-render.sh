#!/bin/bash

# Script to deploy backend to Render.com
# This script helps automate the Render deployment process

echo "🚀 Deploying Backend to Render.com"
echo ""

# Check if render.yaml exists
if [ ! -f "backend/render.yaml" ]; then
    echo "❌ Error: backend/render.yaml not found"
    exit 1
fi

echo "📋 Render Deployment Options:"
echo ""
echo "Option 1: Connect GitHub Repository (Recommended)"
echo "  1. Go to https://dashboard.render.com"
echo "  2. Click 'New +' → 'Web Service'"
echo "  3. Connect your GitHub account"
echo "  4. Select repository: sainisomesh/accessible-housing-matcher"
echo "  5. Render will auto-detect the render.yaml file"
echo "  6. Click 'Create Web Service'"
echo ""
echo "Option 2: Use Render CLI (if installed)"
if command -v render &> /dev/null; then
    echo "  ✅ Render CLI found!"
    echo "  Run: render deploy"
else
    echo "  ⚠️  Render CLI not installed"
    echo "  Install: npm install -g @render/cli"
    echo "  Then: render login"
    echo "  Then: render deploy"
fi
echo ""
echo "Option 3: Manual Setup"
echo "  Follow the guide: docs/BACKEND-RENDER-SETUP.md"
echo ""

# Try to open Render dashboard
echo "🌐 Opening Render dashboard..."
open "https://dashboard.render.com" 2>/dev/null || echo "Please visit: https://dashboard.render.com"

echo ""
echo "📝 Quick Setup Steps:"
echo "  1. Sign up/Login to Render"
echo "  2. New → Web Service"
echo "  3. Connect GitHub → Select: sainisomesh/accessible-housing-matcher"
echo "  4. Root Directory: backend"
echo "  5. Build Command: pip install -r requirements.txt"
echo "  6. Start Command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "  7. Add Environment Variables:"
echo "     - APPS_SCRIPT_URL = (your Apps Script URL)"
echo "     - CORS_ORIGINS = https://sainisomesh.github.io"
echo "  8. Click 'Create Web Service'"
echo ""
echo "✅ Once deployed, update frontend/src/config.js with your Render backend URL!"

