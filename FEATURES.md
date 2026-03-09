# Claude-Git Sync - Complete Feature List

## 🎯 Core Features

### ✅ Branch Syncing
**Auto-sync chat when switching branches**

```bash
git checkout feature-auth
💬 Chat synced to: feature-auth
```

**Features:**
- Automatic via `post-checkout` hook
- Saves current branch chat before switching
- Restores target branch chat after switching
- Hierarchical inheritance (child branches inherit parent)
- Zero manual commands required

---

### ✅ Git Stash Integration ⭐
**Save/restore chat with code stashes**

```bash
git-claude stash push -m "WIP"
💾 Chat context saved with stash

git-claude stash pop
📚 Chat context restored from stash
```

**Features:**
- Chat saved automatically with `git stash push`
- Chat restored automatically with `git stash pop/apply`
- Named stashes supported
- List all stash contexts
- Storage: `.claude-git-sync/stashes/`

---

### ✅ Git Merge Integration ⭐ NEW!
**Merge chat contexts when merging branches**

```bash
git merge feature-payments
🔀 Merging chat contexts...
✓ Chat contexts merged
   Combined: 50 + 30 = 80 messages
```

**Features:**
- Automatic via `post-merge` hook
- Pre-merge backups with commit SHAs
- Appends source branch messages to target
- Merge markers with full metadata
- Commit SHA tracking for precision
- Storage: `.claude-git-sync/merge-backups/`

---

## 🛠️ Installation Modes

### Mode 1: Git Hooks Only (Simplest)
**Zero overhead, fully automatic**

```bash
cp -r src hooks /your/project/
python3 src/setup_integration.py
```

**Triggers:**
- `git checkout` → auto-sync
- `git commit` → auto-save
- `git merge` → auto-merge ⭐
- All automatic, silent

---

### Mode 2: git-claude Wrapper (Best UX)
**Enhanced feedback and control**

```bash
sudo cp git-claude /usr/local/bin/
# Or alias: alias git='git-claude'
```

**Features:**
- `git-claude checkout` → shows sync status
- `git-claude merge` → shows merge details
- `git-claude stash` → handles chat stash
- `git-claude status` → git + chat status
- Enhanced output, better visibility

---

### Mode 3: Shell Function (Most Transparent)
**Complete Git command override**

```bash
bash install-git-wrapper.sh
# Add to ~/.bashrc
source ~/.bashrc
```

**Features:**
- Overrides `git` command completely
- Transparent integration
- No separate binary needed
- Works in all shells

---

## 📁 Storage System

### Branch Sessions
```
.claude-git-sync/sessions/
├── main.jsonl                    # Main branch chat
├── feature-auth.jsonl            # Feature branch chat
└── feature-payments.jsonl        # Another feature chat
```

### Stash Contexts
```
.claude-git-sync/stashes/
├── main-stash-20260309-150000.jsonl
└── feature-auth-WIP.jsonl
```

### Merge Backups ⭐
```
.claude-git-sync/merge-backups/
├── main_a1b2c3d4_before_merge_feature-auth_e5f6g7h8.jsonl
└── main_f9g0h1i2_before_merge_feature-payments_j3k4l5m6.jsonl
       ↑      ↑                           ↑            ↑
    branch  SHA                       source        source
                                      branch         SHA
```

### Metadata
```json
{
  "branches": {
    "main": {
      "sessionId": "...",
      "messageCount": 50,
      "lastBackup": "2026-03-09T..."
    }
  },
  "stashes": {
    "stash-20260309": {
      "branch": "feature-auth",
      "messageCount": 127,
      "created": "2026-03-09T..."
    }
  },
  "mergeBackups": [
    {
      "targetBranch": "main",
      "targetSHA": "a1b2c3d4",
      "sourceBranch": "feature-auth",
      "sourceSHA": "e5f6g7h8",
      "messageCount": 50,
      "timestamp": "2026-03-09T..."
    }
  ]
}
```

---

## 🎮 Commands

### Git Commands (Automatic)
```bash
git checkout <branch>        # Auto-sync
git checkout -b <new>        # Auto-init with inheritance
git commit                   # Auto-save
git merge <branch>           # Auto-merge chats ⭐
```

### git-claude Commands
```bash
git-claude checkout <branch>     # Enhanced sync
git-claude merge <branch>        # Enhanced merge ⭐
git-claude stash push           # Save chat
git-claude stash pop            # Restore chat
git-claude stash list           # Show stashes
git-claude status               # Git + chat status
```

### Python Commands (Manual)
```bash
python3 src/git_sync.py save
python3 src/git_sync.py switch <branch>
python3 src/git_sync.py create <branch>
python3 src/git_sync.py merge <branch>      # ⭐
python3 src/git_sync.py stash-save [name]
python3 src/git_sync.py stash-restore
python3 src/git_sync.py stash-list
python3 src/git_sync.py status
```

---

## 🔍 Technical Details

### Branch Syncing
```
1. You: git checkout feature-auth
2. Hook: .git/hooks/post-checkout
3. Backup: Current chat → .claude-git-sync/sessions/main.jsonl
4. Restore: .claude-git-sync/sessions/feature-auth.jsonl → Active session
5. Result: feature-auth conversation loaded
```

### Stash Syncing
```
1. You: git-claude stash push -m "WIP"
2. Save: Active session → .claude-git-sync/stashes/branch-WIP.jsonl
3. Git: git stash push -m "WIP"
4. Later: git-claude stash pop
5. Restore: Stash file → Active session
6. Git: git stash pop
```

### Merge Syncing ⭐
```
1. You: git merge feature-auth
2. Git: Merges code
3. Hook: .git/hooks/post-merge triggers
4. Backup: Pre-merge state → merge-backups/main_SHA_before_merge_...
5. Merge: Append feature-auth messages to main
6. Marker: Add merge metadata with commit SHAs
7. Result: Combined chat history
```

---

## 📊 Inheritance

```
main (50 messages)
  ↓ git checkout -b feature-auth
feature-auth (inherits 50 → adds 25 = 75 total)
  ↓ git checkout -b bugfix-login
bugfix-login (inherits 75 → adds 10 = 85 total)

# Back to main and merge
main ← git merge feature-auth
main (50 + 75 = 125 messages combined)
```

---

## 🎯 Use Cases

### Feature Development
```bash
# Develop feature with isolated chat
git checkout -b feature-auth
# ... discuss auth with Claude (75 messages)

# Merge when done
git checkout main
git merge feature-auth
✓ Combined: 50 + 75 = 125 messages
```

### Hotfix Workflow
```bash
# Urgent bug during feature work
git-claude stash push -m "feature work"
git checkout main
# Fix bug...
git checkout feature-branch
git-claude stash pop
# Resume with full context
```

### Parallel Features
```bash
main
├── feature-payments (isolated chat)
├── feature-auth (isolated chat)
└── feature-notifications (isolated chat)

# Merge all into main
# Each brings its own chat history
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **START-HERE.md** | Quick start guide |
| **README.md** | Main documentation |
| **INSTALL.md** | Installation guide |
| **QUICKSTART.md** | 5-minute tutorial |
| **SUMMARY.md** | Technical overview |
| **STASH-GUIDE.md** | Stash integration details |
| **MERGE-GUIDE.md** | Merge integration details ⭐ |
| **COMPLETE-GUIDE.md** | Everything combined |
| **FEATURES.md** | This file |

---

## ✅ Complete Feature Matrix

| Feature | Auto | git-claude | Manual | Hooks |
|---------|------|------------|--------|-------|
| **Branch sync** | ✅ | ✅ | ✅ | post-checkout |
| **Branch create** | ✅ | ✅ | ✅ | - |
| **Commit save** | ✅ | ✅ | ✅ | post-commit |
| **Merge sync** ⭐ | ✅ | ✅ | ✅ | post-merge |
| **Stash save** | ⚠️ | ✅ | ✅ | - |
| **Stash restore** | ⚠️ | ✅ | ✅ | - |
| **Inheritance** | ✅ | ✅ | ✅ | - |
| **Status** | - | ✅ | ✅ | - |

⚠️ = Requires git-claude wrapper

---

## 🚀 What Makes This Special

✅ **No manual commands** - Git does everything
✅ **Real Claude integration** - Uses actual `.jsonl` files
✅ **Commit SHA tracking** - Precise merge identification
✅ **Three installation modes** - Choose your style
✅ **Complete Git integration** - checkout, stash, merge all supported
✅ **Automatic backups** - Never lose chat context
✅ **Hierarchical inheritance** - Like Git itself
✅ **Production ready** - Working and tested

---

## 📦 Project Status

**Version**: 1.0
**Status**: Production Ready
**Location**: `~/Desktop/claude-git-sync/`
**Installed**: `/mnt/c/Users/dev/` (working)

**Supported Operations:**
- ✅ git checkout
- ✅ git commit
- ✅ git stash (with wrapper)
- ✅ git merge ⭐ NEW!

**Coming Soon:**
- Configurable merge strategies
- Web UI for viewing chat history
- Branch comparison tools
- Export/import capabilities

---

## 🎉 Summary

**Complete Git-Claude Integration:**
- Branches sync automatically
- Stashes save/restore chats
- Merges combine chat contexts ⭐
- All with commit SHA tracking
- Zero manual intervention
- Works exactly like Git should

**Your code AND conversations, perfectly synchronized!**
