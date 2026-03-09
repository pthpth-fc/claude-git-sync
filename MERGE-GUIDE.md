# Git Merge + Claude Chat Integration

**Your chat contexts now merge automatically with Git merges!**

## What It Does

When you merge Git branches, the chat contexts merge too - completely automatic.

```bash
git merge feature-auth
# Code merges
# Chat contexts merge automatically
✓ Chat contexts merged
```

## How It Works

### Automatic (Recommended)

Just use normal Git merge:

```bash
git checkout main
git merge feature-authentication

# Output:
Merge made by the 'ort' strategy.
 src/auth.py | 45 +++++++++++++++++++++++++++++++++++++++++++++
 1 file changed, 45 insertions(+)

🔀 Merge detected: feature-authentication → main
📝 Merging chat contexts...

💾 Pre-merge backup saved
   Target: main @ a1b2c3d4 (50 messages)

🔀 Merging chat contexts
   feature-authentication @ e5f6g7h8
   → main @ a1b2c3d4
   Common ancestor: 9i0j1k2l

✓ Chat contexts merged
   main: 50 messages
   feature-authentication: 75 messages
   Combined: 125 messages

✅ Code and chat merged successfully!
```

### With git-claude Wrapper

```bash
git-claude merge feature-authentication
# Same as above, with enhanced output
```

## What Gets Merged

### Code Merge (Git's job)

- All commits from feature branch
- File changes
- Conflict resolution (if any)

### Chat Merge (Our job)

- **Pre-merge backup**: Saves current chat state with commit SHAs
- **Merge marker**: Adds metadata about the merge
- **Chat combination**: Appends feature branch messages to main
- **Commit tracking**: Records exact SHAs of both branches

## Merge Strategies

### Default: Append

Messages from both branches are combined:

```
main chat (50 messages)
  +
[MERGE MARKER with commit SHAs]
  +
feature-auth chat (75 messages)
  =
Combined chat (125 messages)
```

### Alternative: Keep (future)

Keep only target branch chat:

```
main chat (50 messages)
  +
[MERGE SUMMARY - feature chat discarded]
  =
main chat (50 messages)
```

## File Storage

### Merge Backups

```
.claude-git-sync/
└── merge-backups/
    └── main_a1b2c3d4_before_merge_feature-auth_e5f6g7h8.jsonl
        ↑      ↑                            ↑          ↑
        |      |                            |          |
      branch  SHA                      source       source
                                      branch        SHA
```

**Filename format**: `{target}_{target-sha}_before_merge_{source}_{source-sha}.jsonl`

### Merge Markers

Added to chat transcript:

```json
{
  "type": "merge-marker",
  "messageId": "merge-1773048000",
  "timestamp": "2026-03-09T17:30:00",
  "mergeInfo": {
    "sourceBranch": "feature-auth",
    "sourceSHA": "e5f6g7h8",
    "targetBranch": "main",
    "targetSHA": "a1b2c3d4",
    "mergeBase": "9i0j1k2l",
    "strategy": "append",
    "sourceMessages": 75,
    "targetMessages": 50
  }
}
```

## Real-World Workflow

### Feature Development → Main

```bash
# Feature branch: developed auth feature with Claude
git checkout feature-authentication
# 2 weeks of work, 75 messages with Claude about auth

# Ready to merge
git checkout main
# Currently: 50 messages about general project

git merge feature-authentication
# Code merged
💾 Pre-merge backup saved
✓ Chat contexts merged
   Combined: 125 messages

# Now main has:
# - Original 50 messages
# - Merge marker
# - 75 auth feature messages
# Full context of both development streams!
```

### Multiple Features

```bash
# Main starts with 50 messages
git checkout main

# Merge feature 1
git merge feature-payments
✓ Combined: 50 + 30 = 80 messages

# Merge feature 2
git merge feature-authentication
✓ Combined: 80 + 75 = 155 messages

# Main now has complete history:
# - Original project context
# - Payment feature discussions
# - Authentication feature discussions
```

## Pre-Merge Backups

Every merge creates a backup before making changes:

```bash
# After several merges
ls .claude-git-sync/merge-backups/

main_a1b2c3d4_before_merge_feature-auth_e5f6g7h8.jsonl
main_f9g0h1i2_before_merge_feature-payments_j3k4l5m6.jsonl
main_n7o8p9q0_before_merge_bugfix-login_r1s2t3u4.jsonl
```

Each backup:
- Exact state before merge
- Identified by commit SHAs
- Full chat transcript
- Can be restored if needed

## Metadata Tracking

```json
{
  "mergeBackups": [
    {
      "targetBranch": "main",
      "targetSHA": "a1b2c3d4",
      "sourceBranch": "feature-auth",
      "sourceSHA": "e5f6g7h8",
      "backupFile": ".claude-git-sync/merge-backups/...",
      "messageCount": 50,
      "timestamp": "2026-03-09T17:30:00"
    }
  ]
}
```

## Integration Points

### 1. Git Hook (post-merge)

Triggers after successful `git merge`:

```bash
.git/hooks/post-merge
  ↓
Detects merged branch
  ↓
Calls: python3 src/git_sync.py merge <branch>
  ↓
Automatic chat merge
```

### 2. git-claude Wrapper

```bash
git-claude merge feature-auth
  ↓
Runs: git merge feature-auth
  ↓
If successful, runs: python3 src/git_sync.py merge feature-auth
  ↓
Seamless integration
```

### 3. Manual Command

```bash
python3 src/git_sync.py merge feature-auth
```

## Conflict Handling

### Code Conflicts

Git handles these - resolve normally:

```bash
git merge feature-auth
# CONFLICT in file.py
# Resolve conflicts
git add file.py
git commit
# post-merge hook runs automatically
✓ Chat contexts merged
```

### Chat "Conflicts"

There are no chat conflicts! We always append, so:
- No conflict resolution needed
- Both chat histories preserved
- Chronological order maintained via markers

## Commands

### Automatic (Just Use Git)

```bash
git merge <branch>
# Chat merges automatically via hook
```

### With Wrapper

```bash
git-claude merge <branch>
# Enhanced output + chat merge
```

### Manual

```bash
# Merge chat contexts
python3 src/git_sync.py merge <source-branch>
```

## Status

View merge history:

```bash
python3 src/git_sync.py status

# Shows merge backups in metadata
ls .claude-git-sync/merge-backups/
```

## Configuration (Future)

Eventually configurable strategies:

```bash
# In .claude-git-sync/config.json
{
  "mergeStrategy": "append",  // or "keep", "summary"
  "createBackups": true,
  "verboseOutput": true
}
```

## Best Practices

### Before Merge

```bash
# Make sure changes are committed
git status

# Check which branch you're merging
git log <feature-branch> --oneline
```

### After Merge

```bash
# Verify chat merge
python3 src/git_sync.py status

# Check merge backup exists
ls .claude-git-sync/merge-backups/
```

### Recover from Merge

If you need to undo a chat merge:

```bash
# Find the backup
ls .claude-git-sync/merge-backups/

# Restore from backup
cp .claude-git-sync/merge-backups/main_*.jsonl \
   ~/.claude/projects/.../current-session.jsonl
```

## Examples

### Example 1: Feature Complete

```bash
$ git checkout main
$ git merge feature-authentication

Updating a1b2c3d..e5f6g7h
Fast-forward
 src/auth.py | 45 ++++++++++++++++++++++++++++++
 1 file changed, 45 insertions(+)

🔀 Merge detected: feature-authentication → main
📝 Merging chat contexts...

💾 Pre-merge backup saved
   Target: main @ a1b2c3d (50 messages)

🔀 Merging chat contexts
   feature-authentication @ e5f6g7h
   → main @ a1b2c3d
   Common ancestor: 9i0j1k2

✓ Chat contexts merged
   main: 50 messages
   feature-authentication: 75 messages
   Combined: 125 messages

✅ Code and chat merged successfully!
```

### Example 2: Multiple Merges

```bash
$ git merge feature-payments
✓ Combined: 50 + 30 = 80 messages

$ git merge feature-notifications
✓ Combined: 80 + 20 = 100 messages

$ python3 src/git_sync.py status
📍 Current Branch: main
   Messages: 100

$ ls .claude-git-sync/merge-backups/
main_a1b2c3d_before_merge_feature-payments_x1y2z3a.jsonl
main_b4c5d6e_before_merge_feature-notifications_f7g8h9i.jsonl
```

## Summary

✅ **git merge** → Chat contexts merge automatically
✅ **Commit SHA tracking** → Precise backup identification
✅ **Pre-merge backups** → Safety net for every merge
✅ **Merge markers** → Full metadata in chat transcript
✅ **Zero manual work** → Completely automatic
✅ **Works with hooks** → Use normal Git commands
✅ **git-claude support** → Enhanced feedback

**Your code AND conversation history, merged together!** 🔀
