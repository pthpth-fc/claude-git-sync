#!/usr/bin/env bash
# Claude Code UserPromptSubmit hook
# Auto-saves current chat state after each user message

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
if [ -z "$CURRENT_BRANCH" ]; then
  exit 0
fi

# Save in background to avoid blocking
python3 "$REPO_ROOT/src/git_sync.py" save &>/dev/null &

exit 0
