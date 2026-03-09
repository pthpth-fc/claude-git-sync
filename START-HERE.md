# 🚀 Claude-Git Sync - Start Here

## What You Asked For

> "I don't want a separate python to run, my git should do it on its own"

## What You Got

**Git that automatically syncs Claude Code chats. No manual commands. Just works.**

```bash
git checkout feature-auth
💬 Chat synced to: feature-auth
```

---

## Quick Start

### Already Installed! ✅

**Location:** `/mnt/c/Users/dev`

**Just use Git:**
```bash
git checkout feature-demo    # → auto-syncs chat
git checkout master          # → auto-syncs back
```

**Check status:**
```bash
python3 src/git_sync.py status
```

---

## Three Ways to Use

### 1. Git Hooks Only (Active Now)

**No wrapper needed. Already working.**

```bash
git checkout <branch>
# → Hook runs automatically
# → Chat syncs in background
```

### 2. git-claude Wrapper (Optional)

**Better visual feedback:**

```bash
# Copy to your PATH
sudo cp ~/Desktop/claude-git-sync/git-claude /usr/local/bin/
chmod +x /usr/local/bin/git-claude

# Use it
git-claude checkout feature-auth
💬 Chat synced to: feature-auth
```

### 3. Shell Function (Most Transparent)

**Override git command:**

```bash
# Run installer
bash ~/Desktop/claude-git-sync/install-git-wrapper.sh
# Choose option 1
# Add to ~/.bashrc
# source ~/.bashrc

# Now your regular git command syncs chats
git checkout <branch>
💬 Chat synced automatically
```

---

## Install in Other Projects

**30 seconds:**

```bash
cd /path/to/your/project
cp -r ~/Desktop/claude-git-sync/src .
cp -r ~/Desktop/claude-git-sync/hooks .
python3 src/setup_integration.py
```

Done! That project now has automatic chat syncing.

---

## How It Works

```
You type: git checkout feature-auth
            ↓
Git runs:  .git/hooks/post-checkout
            ↓
Hook runs: python3 src/git_sync.py auto
            ↓
Script:    1. Backs up current chat
           2. Restores feature-auth chat
            ↓
Claude:    Sees feature-auth conversation
            ↓
You:       Continue where you left off
```

**No manual Python commands. Git handles everything.**

---

## Files

```
~/Desktop/claude-git-sync/
├── git-claude              ← Git wrapper (optional)
├── install-git-wrapper.sh  ← Easy installer
├── src/
│   ├── git_sync.py         ← Main sync engine
│   ├── claude_session_manager.py
│   └── setup_integration.py
├── hooks/
│   ├── post-checkout       ← Auto-sync on branch switch
│   ├── post-commit         ← Auto-save on commit
│   └── prepare-commit-msg
├── START-HERE.md           ← This file
├── README.md               ← Full documentation
├── INSTALL.md              ← Installation guide
├── QUICKSTART.md           ← 5-minute tutorial
└── SUMMARY.md              ← What we built
```

---

## Documentation

- **START-HERE.md** (this file) - Quick overview
- **README.md** - Complete documentation
- **INSTALL.md** - Detailed installation options
- **QUICKSTART.md** - Get running in 5 minutes
- **SUMMARY.md** - Technical overview

---

## Test It Now

**In your terminal:**

```bash
cd /mnt/c/Users/dev

# Create test branch
git checkout -b test-branch
# Watch: Hook runs, chat syncs

# Switch back
git checkout master
# Watch: Hook runs, chat syncs back

# Check what happened
python3 src/git_sync.py status
```

---

## What Makes This Special

✅ **No forking Git** - Uses Git's native hooks
✅ **No manual commands** - Everything automatic
✅ **Real integration** - Uses actual Claude Code session files
✅ **Hierarchical** - Child branches inherit parent context
✅ **Transparent** - Works exactly like Git
✅ **Optional wrapper** - Add better UX if you want
✅ **Your way** - Git does it all automatically

---

## Commands You DON'T Need to Run

❌ `python3 src/git_sync.py switch <branch>`
✅ `git checkout <branch>`  ← Just use this

❌ `python3 src/git_sync.py save`
✅ `git commit`  ← This auto-saves

❌ `python3 src/git_sync.py create <branch>`
✅ `git checkout -b <branch>`  ← This works

**The Python scripts exist for:**
- Manual control (if you want it)
- Status checking
- Behind-the-scenes automation

**You never have to call them manually.**

---

## Share It

```bash
# Copy entire project
cp -r ~/Desktop/claude-git-sync /path/to/share

# Or copy just what's needed
cp -r ~/Desktop/claude-git-sync/{src,hooks} /project/
cd /project && python3 src/setup_integration.py
```

---

## Support

**Not working?**
```bash
ls -la .git/hooks/post-checkout    # Should exist
python3 src/git_sync.py status     # Check state
```

**Want wrapper feedback?**
```bash
bash ~/Desktop/claude-git-sync/install-git-wrapper.sh
```

**Check backups:**
```bash
ls -la .claude-git-sync/sessions/
cat .claude-git-sync/metadata.json
```

---

## The Vision Realized

**You wanted:** Git and Claude to work together seamlessly.

**You got:** A system where:
- Git commands sync chats automatically
- No manual intervention needed
- Works exactly like Git should
- Optional wrapper for better UX
- Real integration with Claude Code

**Mission accomplished.** 🎉

---

## Next Steps

1. ✅ Test it (already working in `/mnt/c/Users/dev`)
2. ✅ Add wrapper (optional - run `install-git-wrapper.sh`)
3. ✅ Copy to other projects (see "Install in Other Projects")
4. ✅ Customize (edit Python scripts as needed)

**Enjoy Git with automatic Claude chat syncing!**

---

**Location:** `~/Desktop/claude-git-sync/`
**Status:** Complete and working
**Installation:** Active in `/mnt/c/Users/dev`
**Ready:** To use and share
