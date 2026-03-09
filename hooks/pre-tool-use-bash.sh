#!/usr/bin/env bash
# Claude Code PreToolUse hook for Bash commands
# Saves the current branch name before any command runs,
# so PostToolUse can detect if a branch switch happened.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

STATE_DIR="$REPO_ROOT/.claude-git-sync"
mkdir -p "$STATE_DIR"

# Save current branch before the command executes
git branch --show-current 2>/dev/null > "$STATE_DIR/.pre-command-branch"

exit 0
