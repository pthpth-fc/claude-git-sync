#!/usr/bin/env bash
# Claude Code hook: onToolCall
# Detects when Git checkout commands are executed

# This hook is triggered after any tool call in Claude Code
# We check if it was a Git branch switch

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
  # Not in a git repo, exit silently
  exit 0
fi

# Check if this was a git checkout command
# (Claude Code might pass tool call info via env vars or args)
# For now, we check the current branch against stored state

STATE_FILE="$REPO_ROOT/.claude/current-branch"
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [ -f "$STATE_FILE" ]; then
  PREVIOUS_BRANCH=$(cat "$STATE_FILE")

  if [ "$CURRENT_BRANCH" != "$PREVIOUS_BRANCH" ]; then
    # Branch changed! Load new chat session
    echo "🔄 Branch switch detected: $PREVIOUS_BRANCH → $CURRENT_BRANCH"
    node "$REPO_ROOT/src/cli.js" switch "$CURRENT_BRANCH"
  fi
fi

# Update stored branch
echo "$CURRENT_BRANCH" > "$STATE_FILE"
