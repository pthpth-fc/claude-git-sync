#!/usr/bin/env bash
# Claude Code hook: onSessionStart
# Loads the appropriate chat session when Claude Code starts

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
  # Not in a git repo
  exit 0
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [ -z "$CURRENT_BRANCH" ]; then
  exit 0
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║         Claude-Git Sync Active                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Current branch: $CURRENT_BRANCH"
echo ""

# Load chat session for current branch
node "$REPO_ROOT/src/cli.js" switch "$CURRENT_BRANCH" 2>/dev/null

# Store current branch
STATE_FILE="$REPO_ROOT/.claude/current-branch"
mkdir -p "$(dirname "$STATE_FILE")"
echo "$CURRENT_BRANCH" > "$STATE_FILE"
