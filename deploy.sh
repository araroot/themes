#!/bin/bash

# Theme Dashboard Deployment Script
# This script generates the static site and deploys to GitHub Pages

set -e  # Exit on error

echo "🚀 Starting deployment process..."

# Check if Excel file exists
if [ ! -f "PF_Ranks.xlsx" ]; then
    echo "❌ Error: PF_Ranks.xlsx not found!"
    echo "Please place the Excel file in this directory first."
    exit 1
fi

# Generate static HTML
echo "📊 Generating static HTML from Excel..."
python export_static.py

# Check if HTML was generated
if [ ! -f "docs/index.html" ]; then
    echo "❌ Error: Failed to generate docs/index.html"
    exit 1
fi

echo "✅ HTML generated successfully"

# Git operations
echo "📝 Committing changes..."
git add docs/index.html PF_Ranks.xlsx

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Update theme dashboard - $(date '+%Y-%m-%d %H:%M')"

    echo "📤 Pushing to GitHub..."
    git push

    echo "✅ Deployment complete!"
    echo "🌐 Your site will be updated at: https://araroot.github.io/themes/"
    echo "⏱️  GitHub Pages may take 1-2 minutes to rebuild"
fi
