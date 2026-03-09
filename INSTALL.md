# Installation Guide - Git with Automatic Claude Chat Sync

## TL;DR - Fastest Setup

```bash
cd ~/Desktop/claude-git-sync
bash install-git-wrapper.sh
```

Choose option 1, add to your shell, done. Now `git checkout` automatically syncs chats.

---

## Three Ways to Install

### Method 1: Transparent Shell Function (Recommended)

Your `git` command automatically syncs chats. No changes to your workflow.

```bash
# Add this to ~/.bashrc or ~/.zshrc
git() {
    local GIT_CMD="$1"
    local BEFORE_BRANCH=$(command git branch --show-current 2>/dev/null || echo "")

    # Find sync script
    local SYNC_SCRIPT=""
    local GIT_ROOT=$(command git rev-parse --show-toplevel 2>/dev/null)
    if [ -n "$GIT_ROOT" ] && [ -f "$GIT_ROOT/src/git_sync.py" ]; then
        SYNC_SCRIPT="$GIT_ROOT/src/git_sync.py"
    fi

    case "$GIT_CMD" in
        checkout|switch)
            command git "$@"
            if [ $? -eq 0 ] && [ -n "$SYNC_SCRIPT" ]; then
                local AFTER_BRANCH=$(command git branch --show-current 2>/dev/null)
                [ "$BEFORE_BRANCH" != "$AFTER_BRANCH" ] && echo "💬 Chat synced to: $AFTER_BRANCH"
            fi
            ;;
        *)
            command git "$@"
            ;;
    esac
}

# Then reload
source ~/.bashrc
```

**Usage:**
```bash
git checkout feature-auth
# → switches branch + syncs chat automatically!
```

---

### Method 2: Use `git-claude` Command

Drop-in replacement for git.

```bash
# Copy git-claude to your PATH
sudo cp git-claude /usr/local/bin/
sudo chmod +x /usr/local/bin/git-claude

# Use it
git-claude checkout feature-auth

# Or alias it (optional)
alias git='git-claude'
```

**Usage:**
```bash
git-claude checkout feature-auth
git-claude commit -m "Update"
git-claude status  # Shows git status + chat status
```

---

### Method 3: Git Hooks Only (No Wrapper)

Just install hooks, use normal `git` commands. Hooks do everything.

```bash
cd your-project
python3 ~/Desktop/claude-git-sync/src/setup_integration.py
```

**Usage:**
```bash
git checkout feature-auth
# → Hook automatically syncs chat!
```

Git hooks handle:
- ✅ `git checkout` → auto-sync chat
- ✅ `git commit` → auto-save chat
- ✅ `git switch` → auto-sync chat

**This is already installed and working in /mnt/c/Users/dev!**

---

## What Each Method Does

| Method | How it works | Pros | Cons |
|--------|-------------|------|------|
| Shell function | Wraps `git` command | Transparent, see feedback | Only in your shell |
| git-claude | Separate binary | Can share with team | Type `git-claude` not `git` |
| Hooks only | Git's native hooks | Zero overhead | Less visible feedback |

---

## Test It

After installing:

```bash
# Check status
git status  # (or git-claude status)

# Create test branch
git checkout -b test-feature

# Switch branches
git checkout master
git checkout test-feature

# You should see:
# 💬 Chat synced to: test-feature
```

---

## Copy to Other Projects

```bash
# From any project:
cp -r ~/Desktop/claude-git-sync/src .
cp -r ~/Desktop/claude-git-sync/hooks .
python3 src/setup_integration.py
```

Now that project has automatic chat syncing!

---

## Uninstall

### Remove shell function
Delete the `git()` function from ~/.bashrc

### Remove git-claude
```bash
sudo rm /usr/local/bin/git-claude
unalias git
```

### Remove hooks
```bash
rm .git/hooks/post-checkout
rm .git/hooks/post-commit
rm -rf .claude-git-sync
```

---

## How It Actually Works

1. **Git Hook** (`post-checkout`) triggers on branch switch
2. **Python Script** backs up current session, restores branch session
3. **Session Files** are real Claude Code `.jsonl` transcripts
4. **No data loss** - everything is backed up locally

```
You: git checkout feature-auth
     ↓
Git Hook: detects branch switch
     ↓
Backup: copies ~/.claude/projects/.../session.jsonl
        → .claude-git-sync/sessions/main.jsonl
     ↓
Restore: copies .claude-git-sync/sessions/feature-auth.jsonl
         → ~/.claude/projects/.../session.jsonl
     ↓
Claude Code: sees new conversation history!
```

---

## Already Set Up?

If you already ran `setup_integration.py` in a project:

**You're done!** Just use `git` normally:
- `git checkout <branch>` → chat syncs automatically
- `git commit` → chat saves automatically

To add the wrapper for better feedback:
```bash
bash install-git-wrapper.sh
```

---

## Troubleshooting

**Not syncing?**
```bash
# Check if hooks installed
ls -la .git/hooks/post-checkout

# Test manually
python3 src/git_sync.py save
python3 src/git_sync.py status
```

**Wrapper not working?**
```bash
# Test the wrapper directly
~/Desktop/claude-git-sync/git-claude status

# Check function is loaded
type git
# Should show "git is a function"
```

---

## Summary

**Simplest**: Use Method 3 (hooks only) - already installed!
**Best UX**: Use Method 1 (shell function) - see all feedback
**Most portable**: Use Method 2 (git-claude binary) - share with team

All three work perfectly. Choose what fits your workflow!
