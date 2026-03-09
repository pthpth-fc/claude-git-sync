#!/usr/bin/env bash
#
# Push Claude-Git Sync to GitHub
#

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Push to GitHub                                      ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Get current directory
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# Check if already has remote
REMOTE=$(git remote -v | grep origin | head -1)

if [ -n "$REMOTE" ]; then
    echo "✓ Remote already configured:"
    git remote -v
    echo ""
    read -p "Push to existing remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push -u origin master
        exit 0
    else
        exit 0
    fi
fi

# No remote - help user create one
echo "No remote configured. Let's set one up!"
echo ""
echo "Step 1: Create a GitHub repository"
echo "────────────────────────────────────────────────────────"
echo ""
echo "Go to: https://github.com/new"
echo ""
echo "Repository name: claude-git-sync"
echo "Description: Automatic Git branch and chat synchronization for Claude Code"
echo "Visibility: Public (recommended) or Private"
echo ""
echo "⚠️  Do NOT initialize with README, .gitignore, or license"
echo "   (we already have these files)"
echo ""
read -p "Press Enter after creating the repository..."
echo ""

# Ask for repository URL
echo "Step 2: Enter your repository URL"
echo "────────────────────────────────────────────────────────"
echo ""
echo "Format: https://github.com/USERNAME/claude-git-sync.git"
echo "   or: git@github.com:USERNAME/claude-git-sync.git"
echo ""
read -p "Repository URL: " REPO_URL

if [ -z "$REPO_URL" ]; then
    echo "❌ No URL provided"
    exit 1
fi

# Add remote
echo ""
echo "Adding remote..."
git remote add origin "$REPO_URL"

# Verify
echo ""
echo "✓ Remote added:"
git remote -v

# Push
echo ""
echo "Step 3: Pushing to GitHub"
echo "────────────────────────────────────────────────────────"
echo ""

# Check if main or master
BRANCH=$(git branch --show-current)
echo "Pushing branch: $BRANCH"
echo ""

git push -u origin "$BRANCH"

PUSH_STATUS=$?

if [ $PUSH_STATUS -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════╗"
    echo "║   ✅ Successfully Pushed to GitHub!                    ║"
    echo "╚════════════════════════════════════════════════════════╝"
    echo ""

    # Extract repo URL for browser
    REPO_WEB=$(echo "$REPO_URL" | sed 's/\.git$//' | sed 's/git@github.com:/https:\/\/github.com\//')

    echo "Your repository: $REPO_WEB"
    echo ""
    echo "Next steps:"
    echo "  • View on GitHub: $REPO_WEB"
    echo "  • Clone elsewhere: git clone $REPO_URL"
    echo "  • Share with others: Send them the GitHub link"
    echo ""
else
    echo ""
    echo "❌ Push failed!"
    echo ""
    echo "Common issues:"
    echo "  • Authentication: Set up GitHub credentials"
    echo "  • Repository exists but isn't empty: Force push with -f (careful!)"
    echo "  • Wrong URL: Check the repository URL"
    echo ""
    echo "Try:"
    echo "  git push -u origin $BRANCH"
    echo ""
fi
