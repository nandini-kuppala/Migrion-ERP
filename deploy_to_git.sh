#!/bin/bash

echo "============================================"
echo "Migrion - Git Deployment Script"
echo "============================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "ERROR: Git is not installed!"
    echo "Please install Git from https://git-scm.com/"
    exit 1
fi

echo "Step 1: Initializing Git repository..."
git init
echo ""

echo "Step 2: Adding all files to Git..."
git add .
echo ""

echo "Step 3: Creating initial commit..."
git commit -m "Initial commit - Migrion ERP Migration Platform"
echo ""

echo "Step 4: Setting main branch..."
git branch -M main
echo ""

echo "Step 5: Adding GitHub remote..."
git remote add origin git@github.com:nandini-kuppala/Migrion-ERP.git
echo ""

echo "Step 6: Pushing to GitHub..."
git push -u origin main

if [ $? -ne 0 ]; then
    echo ""
    echo "============================================"
    echo "WARNING: Push failed!"
    echo "============================================"
    echo ""
    echo "Possible reasons:"
    echo "1. SSH key not configured"
    echo "2. Repository doesn't exist"
    echo "3. No network connection"
    echo ""
    echo "Try using HTTPS instead:"
    echo "git remote set-url origin https://github.com/nandini-kuppala/Migrion-ERP.git"
    echo "git push -u origin main"
    echo ""
    exit 1
fi

echo ""
echo "============================================"
echo "SUCCESS: Pushed to GitHub!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Go to https://share.streamlit.io/"
echo "2. Sign in with GitHub"
echo "3. Click 'New app'"
echo "4. Select your repository: nandini-kuppala/Migrion-ERP"
echo "5. Set main file: app.py"
echo "6. Add secrets (GEMINI_API_KEY and MONGODB_URI)"
echo "7. Deploy!"
echo ""
echo "Your repository: https://github.com/nandini-kuppala/Migrion-ERP"
echo ""
