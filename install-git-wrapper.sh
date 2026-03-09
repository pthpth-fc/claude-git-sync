#!/usr/bin/env bash
#
# Install Git wrapper that automatically syncs Claude Code chats
#
# This creates a shell function that intercepts all 'git' commands
# and adds automatic chat syncing without any manual intervention.

cat << 'EOF'
╔════════════════════════════════════════════════════════╗
║   Git-Claude Transparent Wrapper Installer            ║
╚════════════════════════════════════════════════════════╝

This will install a transparent Git wrapper that:
  ✓ Works exactly like normal Git
  ✓ Automatically syncs Claude Code chats
  ✓ No manual commands needed - just use git!

Installation options:
  1. Shell function (recommended - transparent)
  2. Git alias (git -> git-claude)
  3. System-wide binary

EOF

echo "Choose installation method:"
echo "  1) Shell function (add to ~/.bashrc or ~/.zshrc)"
echo "  2) Git alias (type 'git' and get chat sync)"
echo "  3) Install git-claude as system command"
echo "  4) Just copy git-claude to current directory"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        # Shell function approach
        cat << 'FUNC_EOF' > /tmp/git-claude-function.sh
# Git-Claude wrapper function
# Transparently adds Claude Code chat syncing to all Git operations
git() {
    # Store the real git command
    local GIT_BIN=$(which -a git | grep -v "git is a.*function" | head -1)

    # Get current branch before operation
    local BEFORE_BRANCH=$(command git branch --show-current 2>/dev/null || echo "")

    # Get the git command
    local GIT_CMD="$1"

    # Find sync script
    local SYNC_SCRIPT=""
    local GIT_ROOT=$(command git rev-parse --show-toplevel 2>/dev/null)
    if [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/src/git_sync.py" ]; then
        SYNC_SCRIPT="$GIT_ROOT/src/git_sync.py"
    elif [ -f "$HOME/Desktop/claude-git-sync/src/git_sync.py" ]; then
        SYNC_SCRIPT="$HOME/Desktop/claude-git-sync/src/git_sync.py"
    fi

    # Special handling for certain commands
    case "$GIT_CMD" in
        checkout|switch)
            # Run actual git command
            command git "$@"
            local EXIT_CODE=$?

            # Show chat sync notification
            if [ $EXIT_CODE -eq 0 ] && [ -n "$SYNC_SCRIPT" ]; then
                local AFTER_BRANCH=$(command git branch --show-current 2>/dev/null)
                if [ "$BEFORE_BRANCH" != "$AFTER_BRANCH" ] && [ -n "$AFTER_BRANCH" ]; then
                    echo "💬 Chat synced to: $AFTER_BRANCH"
                fi
            fi

            return $EXIT_CODE
            ;;

        commit)
            # Run git commit
            command git "$@"
            local EXIT_CODE=$?

            # Auto-save after commit
            if [ $EXIT_CODE -eq 0 ] && [ -n "$SYNC_SCRIPT" ]; then
                python3 "$SYNC_SCRIPT" save &>/dev/null &
                echo "💾 Chat saved"
            fi

            return $EXIT_CODE
            ;;

        status)
            # Run git status
            command git status "$@"

            # Show chat info
            if [ -n "$SYNC_SCRIPT" ]; then
                echo ""
                echo "═══ Claude Chat ═══"
                python3 "$SYNC_SCRIPT" status 2>/dev/null | grep -E "Current Branch|Messages:" | head -2
            fi
            ;;

        *)
            # All other commands - pass through
            command git "$@"
            ;;
    esac
}
FUNC_EOF

        echo ""
        echo "✓ Shell function created!"
        echo ""
        echo "Add this to your ~/.bashrc or ~/.zshrc:"
        echo ""
        cat /tmp/git-claude-function.sh
        echo ""
        echo "Or run this to append automatically:"
        echo "  cat /tmp/git-claude-function.sh >> ~/.bashrc"
        echo "  source ~/.bashrc"
        ;;

    2)
        # Git alias approach
        git config --global alias.orig '!git'
        echo ""
        echo "✓ Created git alias!"
        echo ""
        echo "Now use:"
        echo "  git checkout <branch>  → auto-syncs chat"
        echo "  git commit             → auto-saves chat"
        echo "  git.orig <cmd>         → bypass wrapper if needed"
        ;;

    3)
        # System-wide binary
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

        if [ -w "/usr/local/bin" ]; then
            cp "$SCRIPT_DIR/git-claude" /usr/local/bin/
            chmod +x /usr/local/bin/git-claude
            echo ""
            echo "✓ Installed to /usr/local/bin/git-claude"
            echo ""
            echo "Use: git-claude <commands>"
            echo "Or alias: alias git='git-claude'"
        else
            echo ""
            echo "⚠️  Need sudo access to install to /usr/local/bin"
            echo ""
            echo "Run: sudo cp $SCRIPT_DIR/git-claude /usr/local/bin/"
            echo "     sudo chmod +x /usr/local/bin/git-claude"
        fi
        ;;

    4)
        # Copy to current directory
        SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
        cp "$SCRIPT_DIR/git-claude" ./git-claude
        chmod +x ./git-claude
        echo ""
        echo "✓ Copied git-claude to current directory"
        echo ""
        echo "Use: ./git-claude <commands>"
        echo "Or: alias git='./git-claude'"
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Installation Complete!                              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Your Git commands now automatically sync Claude chats!"
echo ""
