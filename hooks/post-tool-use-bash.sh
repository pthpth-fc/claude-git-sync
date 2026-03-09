#!/usr/bin/env bash
# Claude Code PostToolUse hook for Bash commands
# Detects branch switches and injects previous chat context
# so Claude seamlessly has the right conversation history.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

STATE_DIR="$REPO_ROOT/.claude-git-sync"
PRE_BRANCH_FILE="$STATE_DIR/.pre-command-branch"

# If no pre-command state was saved, nothing to do
if [ ! -f "$PRE_BRANCH_FILE" ]; then
  exit 0
fi

PREVIOUS_BRANCH=$(cat "$PRE_BRANCH_FILE" 2>/dev/null)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

# Clean up the temp file
rm -f "$PRE_BRANCH_FILE"

# If branch didn't change, nothing to do
if [ "$PREVIOUS_BRANCH" = "$CURRENT_BRANCH" ] || [ -z "$PREVIOUS_BRANCH" ] || [ -z "$CURRENT_BRANCH" ]; then
  exit 0
fi

# Branch changed! Run the context switch script
python3 "$REPO_ROOT/src/branch_context_loader.py" \
  --repo-root "$REPO_ROOT" \
  --previous-branch "$PREVIOUS_BRANCH" \
  --current-branch "$CURRENT_BRANCH"
