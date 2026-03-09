# Claude-Git Sync

**Automatic synchronization between Git branches and Claude Code chat sessions.**

Just use Git normally. Your chats sync automatically. No manual commands needed.

```bash
git checkout feature-auth
💬 Chat synced to: feature-auth

git stash push -m "work in progress"
💾 Chat context saved with stash

git stash pop
📚 Chat context restored from stash
```

---

## What It Does

- ✅ **Each Git branch has its own chat history**
- ✅ **Switching branches switches your chat automatically**
- ✅ **Child branches inherit parent chat context**
- ✅ **Git stash saves/restores chat context** ⭐ NEW!
- ✅ **All your Git commands work exactly the same**
- ✅ **No manual commands - completely transparent**

---

## Quick Start

### Install in 30 seconds:

```bash
cd your-project
cp -r ~/Desktop/claude-git-sync/src .
cp -r ~/Desktop/claude-git-sync/hooks .
python3 src/setup_integration.py
```

Done! Now use Git normally - chat syncing is automatic.

### Optional: Add wrapper for better feedback

```bash
bash ~/Desktop/claude-git-sync/install-git-wrapper.sh
```

Choose option 1, add to shell config, reload.

---

## How It Works

**Without you doing anything:**

1. You: `git checkout feature-auth`
2. Git hook: detects branch switch
3. System: backs up current chat, restores feature-auth chat
4. Claude Code: sees feature-auth conversation history
5. You: continue conversation from where you left off

**Technical:**
- Git hooks (`post-checkout`, `post-commit`) trigger on Git operations
- Python script backs up/restores Claude Code's `.jsonl` session files
- Sessions stored in `.claude-git-sync/sessions/{branch}.jsonl`
- Hierarchical inheritance: child branches inherit parent chat context

---

## Example Workflow

```bash
# Start on main, chat with Claude about architecture
$ git branch
* main

$ # Chat with Claude about general architecture...

# Create feature branch
$ git checkout -b feature-authentication

💬 Chat synced to: feature-authentication
📚 Inherited 50 messages from main

$ # Chat with Claude about auth implementation...
$ # (Claude has context from main + your new auth discussion)

# Switch to different feature
$ git checkout -b feature-payments

💬 Chat synced to: feature-payments
📚 Inherited 50 messages from main

$ # Chat about payments (doesn't see auth work)

# Go back to auth branch
$ git checkout feature-authentication

💬 Chat synced to: feature-authentication
✓ Restored 75 messages

$ # Auth conversation is exactly as you left it!

# Back to main
$ git checkout main

💬 Chat synced to: main
✓ Restored 50 messages

$ # Main branch chat - no feature work visible
```

---

## Installation Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| **Hooks Only** | Git hooks do everything | Default - already works! |
| **Shell Function** | Wrap `git` command | Better feedback messages |
| **git-claude Binary** | Drop-in replacement | Share with team |

See [INSTALL.md](INSTALL.md) for detailed instructions.

---

## Files

```
claude-git-sync/
├── git-claude                    # Git wrapper binary
├── install-git-wrapper.sh        # Interactive installer
├── src/
│   ├── git_sync.py              # Main sync engine
│   ├── claude_session_manager.py # Session backup/restore
│   └── setup_integration.py     # One-command setup
├── hooks/
│   ├── post-checkout            # Auto-sync on branch switch
│   ├── post-commit              # Auto-save after commit
│   └── prepare-commit-msg       # Pre-commit sync
├── README.md                     # This file
├── INSTALL.md                    # Detailed installation
├── QUICKSTART.md                 # 5-minute guide
├── STASH-GUIDE.md                # Git stash integration ⭐
└── STASH-SUMMARY.md              # Stash quick reference
```

---

## Commands (if needed)

You don't normally need these - hooks handle everything!

But if you want manual control:

```bash
# Check sync status
python3 src/git_sync.py status

# Manual save
python3 src/git_sync.py save

# Manual branch switch
python3 src/git_sync.py switch <branch>

# Create branch with inheritance
python3 src/git_sync.py create <new-branch>
```

---

## Real Integration

This isn't a toy - it works with real Claude Code session files:

- **Location**: `~/.claude/projects/{project}/{sessionId}.jsonl`
- **Format**: JSON Lines - one message per line
- **Content**: Full conversation history (messages, tools, context)
- **Backup**: `.claude-git-sync/sessions/{branch}.jsonl`
- **Restore**: Copies backup over active session

When you switch branches, Claude Code immediately sees the new conversation history. No restart needed.

---

## Inheritance Example

```
main (50 messages about project setup)
  ↓
  ├── feature-auth (inherits 50 + adds 25 auth msgs = 75 total)
  │     ↓
  │     └── bugfix-login (inherits all 75 + adds 10 = 85 total)
  │
  └── feature-api (inherits 50 from main + adds 30 API msgs = 80 total)
```

Just like Git branches inherit commits, chat sessions inherit messages.

---

## Already Installed?

**In `/mnt/c/Users/dev` - already working!**

Just use:
- `git checkout <branch>` → auto-syncs
- `git commit` → auto-saves

To add wrapper for better feedback:
```bash
bash ~/Desktop/claude-git-sync/install-git-wrapper.sh
```

---

## Troubleshooting

**Not syncing?**
```bash
ls -la .git/hooks/post-checkout   # Should exist
python3 src/git_sync.py status     # Check status
```

**Want to see what's happening?**
```bash
bash install-git-wrapper.sh  # Install wrapper for feedback
```

**Check backups:**
```bash
ls -la .claude-git-sync/sessions/
cat .claude-git-sync/metadata.json
```

---

## Uninstall

```bash
rm .git/hooks/post-checkout .git/hooks/post-commit
rm -rf .claude-git-sync src hooks
```

---

## Philosophy

**Git tracks your code across branches.**
**Claude-Git Sync tracks your conversations across branches.**

Each branch has its own development context - both code AND conversation. This tool keeps them synchronized.

---

## Technical Details

### Session Discovery
Finds Claude Code sessions in `~/.claude/projects/` by:
1. Converting project path to directory name (`/mnt/c/Users/dev` → `-mnt-c-Users-dev`)
2. Reading `sessions-index.json` for active session ID
3. Locating transcript file `{sessionId}.jsonl`

### Backup Process
```python
# On branch switch FROM main TO feature:
1. Copy ~/.claude/projects/.../current-session.jsonl
   → .claude-git-sync/sessions/main.jsonl

2. Copy .claude-git-sync/sessions/feature.jsonl
   → ~/.claude/projects/.../current-session.jsonl

3. Update metadata.json with counts and timestamps
```

### Inheritance
When creating a new branch:
```python
# feature-auth created from main:
1. Copy .claude-git-sync/sessions/main.jsonl
   → .claude-git-sync/sessions/feature-auth.jsonl

2. Record parent: metadata["branches"]["feature-auth"]["parentBranch"] = "main"
```

---

## Contributing

Found a bug? Want a feature?

Open an issue or PR at the repository.

---

## License

MIT

---

## Credits

Built for developers who wanted Git and Claude Code to work together seamlessly.

**No more losing conversation context when switching branches!**
