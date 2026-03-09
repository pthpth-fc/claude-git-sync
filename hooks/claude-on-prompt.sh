#!/usr/bin/env bash
# Claude Code hook: onUserPromptSubmit
# Auto-saves chat state after user interactions

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)

if [ -z "$REPO_ROOT" ]; then
  exit 0
fi

# Trigger save (in background to not block)
node "$REPO_ROOT/src/cli.js" save &> /dev/null &
