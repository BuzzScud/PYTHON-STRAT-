#!/bin/bash

# Quick GitHub Deployment Script for ICT Trading System
# This script helps you push your code to GitHub quickly

echo "🚀 ICT Trading System - GitHub Deployment Helper"
echo "=================================================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Get GitHub username
echo ""
echo "📝 Please enter your GitHub username:"
read -p "GitHub Username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required!"
    exit 1
fi

# Confirm repository name
REPO_NAME="ict-trading-system"
echo ""
echo "📁 Repository name will be: $REPO_NAME"
echo "🔗 Full repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "Is this correct? (y/N): " confirm

if [[ ! "$confirm" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

echo ""
echo "🔄 Preparing for GitHub deployment..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run this from your project directory."
    exit 1
fi

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    echo "⚠️  Remote 'origin' already exists. Removing it..."
    git remote remove origin
fi

# Add GitHub remote
echo "🔗 Adding GitHub remote..."
git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Check if there are any changes to commit
if ! git diff-index --quiet HEAD --; then
    echo "📝 Committing latest changes..."
    git add .
    git commit -m "Prepare for live deployment - $(date)"
fi

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
echo ""
echo "🔐 You may be prompted for your GitHub credentials:"
echo "   - Username: $GITHUB_USERNAME"
echo "   - Password: Use your GitHub Personal Access Token (not your password)"
echo ""

if git push -u origin main; then
    echo ""
    echo "✅ SUCCESS! Your code is now on GitHub!"
    echo ""
    echo "🎯 Next Steps:"
    echo "1. Go to: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo "2. Verify your code is there"
    echo "3. Go to: https://share.streamlit.io"
    echo "4. Click 'New app'"
    echo "5. Select your repository: $GITHUB_USERNAME/$REPO_NAME"
    echo "6. Main file path: interfaces/bloomberg_ui.py"
    echo "7. Click Deploy!"
    echo ""
    echo "🌐 Your trading system will be live at:"
    echo "   https://your-app-name.streamlit.app"
    echo ""
    echo "=================================================="
    echo "🚀 Ready for Streamlit Cloud deployment!"
    echo "=================================================="
else
    echo ""
    echo "❌ Push failed. Common solutions:"
    echo ""
    echo "1. 📁 Create the repository on GitHub first:"
    echo "   - Go to https://github.com/new"
    echo "   - Repository name: $REPO_NAME"
    echo "   - Make it PUBLIC"
    echo "   - Don't initialize with README"
    echo "   - Click 'Create repository'"
    echo ""
    echo "2. 🔐 Check your credentials:"
    echo "   - Use Personal Access Token instead of password"
    echo "   - Generate at: https://github.com/settings/tokens"
    echo ""
    echo "3. 🔄 Try running this script again"
    echo ""
fi
