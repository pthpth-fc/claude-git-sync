#!/usr/bin/env bash
# Demo script for Claude-Git Sync

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║      Claude-Git Sync Demo                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

cd ~/Desktop/claude-git-sync

echo "📦 Step 1: Running setup..."
node src/setup.js

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Step 2: Check initial status"
node src/cli.js status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌿 Step 3: Create feature branch with chat inheritance"
node src/cli.js create feature-authentication

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Step 4: Check status after branch creation"
node src/cli.js status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌿 Step 5: Create another feature branch"
node src/cli.js create feature-api

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 Step 6: Switch back to authentication feature"
git checkout feature-authentication
echo "(Git hook should trigger automatically)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔄 Step 7: Switch to main"
git checkout master

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Step 8: Final status"
node src/cli.js status

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 Step 9: Show directory structure"
echo ""
echo ".claude directory contents:"
tree .claude 2>/dev/null || find .claude -type f

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  ✅ Demo Complete!                                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Try these commands:"
echo "  • node src/cli.js status"
echo "  • git checkout feature-authentication"
echo "  • node src/cli.js create my-feature"
