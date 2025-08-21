#!/bin/bash
# Auto-add and commit all Python files and important project files

echo "🔍 Checking for untracked files..."

# Add all Python files
git add *.py
git add src/**/*.py
git add templates/*.html
git add static/**/*
git add requirements.txt
git add README.md
git add *.sh
git add *.json
git add *.yaml
git add *.yml

# Show what will be committed
echo "📋 Files to be committed:"
git status --short

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "✅ No new files to commit"
else
    echo "📝 Committing new files..."
    git commit -m "Auto-add new project files

Added untracked Python files and project resources

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
    
    echo "✅ Files committed!"
    echo ""
    echo "📤 Don't forget to push:"
    echo "   git push origin master"
fi