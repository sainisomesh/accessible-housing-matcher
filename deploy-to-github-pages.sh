#!/bin/bash

# Script to deploy frontend to GitHub Pages
# Run this script after you've created a GitHub repository

echo "🚀 Deploying Frontend to GitHub Pages"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Git not initialized. Run: git init"
    exit 1
fi

# Get GitHub repo URL
if [ -z "$1" ]; then
    echo "📝 Please provide your GitHub repository URL"
    echo "   Usage: ./deploy-to-github-pages.sh https://github.com/username/repo-name.git"
    echo ""
    echo "   Or if you want to set it up manually:"
    echo "   1. Create a new repository on GitHub"
    echo "   2. Copy the repository URL"
    echo "   3. Run: git remote add origin YOUR_REPO_URL"
    echo "   4. Run: ./deploy-to-github-pages.sh"
    exit 1
fi

GITHUB_REPO_URL=$1

# Add remote if it doesn't exist
if ! git remote get-url origin &>/dev/null; then
    echo "➕ Adding GitHub remote..."
    git remote add origin "$GITHUB_REPO_URL"
else
    echo "✅ GitHub remote already exists"
    git remote set-url origin "$GITHUB_REPO_URL"
fi

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm install
npm run build
cd ..

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📝 Creating .gitignore..."
    cat > .gitignore << EOF
# Dependencies
node_modules/
frontend/node_modules/
backend/venv/
backend/__pycache__/
*.pyc

# Build outputs
frontend/dist/
backend/*.db
backend/*.db-journal

# Environment files
.env
backend/.env
*.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
fi

# Add all files
echo "📦 Adding files to git..."
git add .

# Commit
echo "💾 Committing changes..."
git commit -m "Initial commit: Accessible Housing Matcher with GitHub Pages deployment" || echo "No changes to commit"

# Push to main branch
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Go to your GitHub repository: $GITHUB_REPO_URL"
echo "2. Click 'Settings' → 'Pages'"
echo "3. Under 'Source', select 'GitHub Actions'"
echo "4. Wait for the GitHub Actions workflow to run (check the 'Actions' tab)"
echo "5. Your site will be live at: https://YOUR_USERNAME.github.io/REPO_NAME"
echo ""
echo "🔗 Once deployed, update frontend/src/config.js with your Render backend URL"

