# Git Stash + Claude Chat Integration

**Your chat context is now saved and restored with Git stashes!**

## What It Does

When you stash your code changes, your Claude chat context is saved too. When you pop/apply the stash, your chat is restored to match your code.

```bash
git stash push -m "work in progress"
💾 Chat context saved with stash

git stash pop
📚 Chat context restored from stash
```

---

## How It Works

### Automatic Mode (with git-claude wrapper)

```bash
# Stash your work
git-claude stash push -m "auth feature WIP"
# → Saves code changes
# → Saves chat context automatically
💾 Chat context saved with stash

# Work on something else...
git-claude checkout hotfix

# Come back and restore
git-claude stash pop
# → Restores code changes
# → Restores chat context automatically
📚 Chat context restored from stash
```

### Manual Mode (without wrapper)

```bash
# Before stashing
python3 src/git_sync.py stash-save "auth-work"

# Stash your changes
git stash push -m "auth feature WIP"

# Later, before popping
python3 src/git_sync.py stash-restore

# Pop the stash
git stash pop
```

---

## Commands

### With git-claude Wrapper

```bash
# Save with stash
git-claude stash push -m "my work"
git-claude stash save

# Restore from stash
git-claude stash pop
git-claude stash apply

# List stashes (shows code + chat)
git-claude stash list
```

### Manual Python Commands

```bash
# Save chat context
python3 src/git_sync.py stash-save "optional-name"

# Restore most recent stash context
python3 src/git_sync.py stash-restore

# Restore specific stash
python3 src/git_sync.py stash-restore "stash-20260309-153000"

# List all stash contexts
python3 src/git_sync.py stash-list
```

---

## Use Cases

### 1. Quick Context Switch

```bash
# Working on feature, urgent bug comes up
$ git-claude stash push -m "feature work"
💾 Chat context saved with stash

$ git-claude checkout main
💬 Chat synced to: main

# Fix the bug...

$ git-claude checkout feature-branch
$ git-claude stash pop
📚 Chat context restored from stash
# Continue feature work with full context
```

### 2. Experiment Safely

```bash
# Save current state before experimenting
$ git-claude stash push -m "before experiment"
💾 Chat context saved with stash

# Try something risky...
# Chat with Claude about the experiment

# Didn't work? Restore everything
$ git-claude stash pop
📚 Chat context restored
# Back to where you were, including conversation
```

### 3. Interrupt-Driven Development

```bash
# Deep in a feature discussion with Claude
$ git-claude stash push -m "feature-auth deep dive"
💾 Saved: code + 127 message chat history

# Handle interruption on another branch...

# Resume days later
$ git-claude checkout feature-auth
$ git-claude stash pop
📚 Restored: exact conversation state
# Continue as if no interruption happened
```

---

## What Gets Saved

**Code:**
- Uncommitted changes (via `git stash`)
- Staged files
- Working directory state

**Chat:**
- Full conversation history
- All messages exchanged with Claude
- Tool calls and results
- Complete context at time of stash

**Both stored together, restored together!**

---

## How Stash Contexts Are Stored

```
.claude-git-sync/
├── stashes/
│   ├── main-stash-20260309-153000.jsonl
│   ├── feature-auth-stash-20260309-160000.jsonl
│   └── ...
└── metadata.json
```

Each stash gets:
- Branch name
- Timestamp
- Message count
- Full `.jsonl` transcript

---

## Status Command Shows Stashes

```bash
$ python3 src/git_sync.py status

╔════════════════════════════════════════════════════════╗
║         Claude-Git Sync Status                        ║
╚════════════════════════════════════════════════════════╝

📍 Current Branch: feature-auth
   Messages: 75

📊 Total Tracked Branches: 3

Branch Sessions:
────────────────────────────────────────────────────────
→ feature-auth
   Messages: 75

  main
   Messages: 50

💾 Saved Stashes:
────────────────────────────────────────────────────────
  stash-20260309-160000
   Branch: feature-auth
   Messages: 127
   Created: 2026-03-09 16:00:00

  stash-20260309-153000
   Branch: main
   Messages: 50
   Created: 2026-03-09 15:30:00

────────────────────────────────────────────────────────
```

---

## Installation

### Using git-claude Wrapper (Recommended)

Stash support is built-in! Just use `git-claude stash`:

```bash
# Install git-claude
sudo cp ~/Desktop/claude-git-sync/git-claude /usr/local/bin/
sudo chmod +x /usr/local/bin/git-claude

# Or alias it
alias git='git-claude'

# Use stash commands normally
git stash push -m "work"
git stash pop
```

### Without Wrapper

Use manual Python commands before/after stashing:

```bash
# Before stash
python3 src/git_sync.py stash-save

# Do git stash
git stash push

# Before pop
python3 src/git_sync.py stash-restore

# Do git pop
git stash pop
```

---

## Advanced Usage

### Named Stashes

```bash
# Save with meaningful name
git-claude stash push -m "auth-refactor-midpoint"
💾 Chat saved as: auth-refactor-midpoint

# Later, list and find it
git-claude stash list
# Shows your named stash

# Restore specific one
python3 src/git_sync.py stash-restore "auth-refactor-midpoint"
```

### Multiple Stashes

```bash
# Stack multiple stashes
git-claude stash push -m "experiment 1"
git-claude stash push -m "experiment 2"
git-claude stash push -m "experiment 3"

# List all (most recent first)
python3 src/git_sync.py stash-list

# Restore most recent
git-claude stash pop

# Or restore specific one
python3 src/git_sync.py stash-restore "stash-20260309-160000"
git stash apply stash@{1}
```

---

## Workflow Examples

### Scenario: Feature Work Interrupted

```bash
# Monday: Working on complex feature
$ # 2 hours of discussion with Claude...
$ git-claude stash push -m "feature-halfway"
💾 Saved: code + 87 messages

# Tuesday: Urgent production bug
$ git-claude checkout main
$ # Fix bug, deploy, etc.

# Wednesday: Back to feature
$ git-claude checkout feature-branch
$ git-claude stash pop
📚 Restored 87 messages
$ # Continue exactly where you left off!
```

### Scenario: A/B Testing Approaches

```bash
# Try approach A
$ # Chat with Claude about approach A...
$ git-claude stash push -m "approach-A"
💾 Saved

# Try approach B
$ git reset --hard HEAD
$ # Chat with Claude about approach B...
$ git-claude stash push -m "approach-B"
💾 Saved

# Compare both later
$ python3 src/git_sync.py stash-list
# See both approaches with message counts

# Choose one
$ git-claude stash apply
$ python3 src/git_sync.py stash-restore "approach-A"
# Resume approach A with full context
```

---

## Troubleshooting

**Stash not saving?**
```bash
# Check if git-claude is being used
which git-claude

# Or save manually
python3 src/git_sync.py stash-save "my-work"
```

**Can't find stash context?**
```bash
# List all stashes
python3 src/git_sync.py stash-list

# Check storage
ls -la .claude-git-sync/stashes/
```

**Wrong context restored?**
```bash
# List and choose specific one
python3 src/git_sync.py stash-list
python3 src/git_sync.py stash-restore "specific-stash-ref"
```

---

## Comparison: Stash vs Branch

| Feature | Branch Sync | Stash Sync |
|---------|-------------|------------|
| **When** | Switching branches | Temporary save |
| **Storage** | `.claude-git-sync/sessions/` | `.claude-git-sync/stashes/` |
| **Automatic** | Yes (via hook) | Yes (via wrapper) |
| **Use Case** | Long-term work | Short-term save |
| **Restore** | On checkout | On pop/apply |

**Use branches** for parallel workstreams.
**Use stashes** for temporary saves and interruptions.

---

## Implementation Details

### What git-claude Does

```bash
git-claude stash push
  ↓
1. Extract stash message (if provided)
2. Run: python3 src/git_sync.py stash-save "message"
3. Run: git stash push
4. Show: 💾 Chat context saved with stash

git-claude stash pop
  ↓
1. Run: git stash pop
2. Run: python3 src/git_sync.py stash-restore
3. Show: 📚 Chat context restored from stash
```

### Storage Format

```json
{
  "stashes": {
    "stash-20260309-153000": {
      "branch": "feature-auth",
      "backupFile": ".claude-git-sync/stashes/feature-auth-stash-20260309-153000.jsonl",
      "messageCount": 127,
      "created": "2026-03-09T15:30:00",
      "sessionId": "abc-def-ghi"
    }
  }
}
```

---

## Summary

✅ **Stash code** → Chat context saved automatically
✅ **Pop/apply stash** → Chat context restored automatically
✅ **Works with git-claude** → Fully automatic
✅ **Works manually** → Full control with Python commands
✅ **Named stashes** → Easy identification
✅ **Multiple stashes** → Stack as many as you need
✅ **Status command** → See all stash contexts

**Your code AND conversation context, perfectly synchronized!**
