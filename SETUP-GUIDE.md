# Claude Git Sync - Complete Setup & Usage Guide

A step-by-step guide to install, configure, and use Claude Git Sync to automatically manage Claude Code chat sessions across Git branches.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Basic Usage](#basic-usage)
5. [Advanced Usage](#advanced-usage)
6. [VS Code Extension](#vs-code-extension)
7. [Real-World Workflows](#real-world-workflows)
8. [Command Reference](#command-reference)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before installing, ensure you have:

| Requirement   | Minimum Version | Check Command         |
|---------------|----------------|-----------------------|
| Python        | 3.7+           | `python3 --version`   |
| Git           | 2.0+           | `git --version`       |
| Claude Code   | Latest         | `claude --version`    |
| Node.js       | 16+ (optional) | `node --version`      |
| VS Code       | 1.80+ (optional)| `code --version`     |

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/claude-git-sync.git
cd claude-git-sync
```

### Step 2: Install Git Hooks

Navigate to your **target project** (the repo where you want chat syncing) and run:

```bash
python3 /path/to/claude-git-sync/src/setup_integration.py
```

This will:
- Create the `.claude-git-sync/` directory in your project
- Install Git hooks (`post-checkout`, `post-commit`, `post-merge`, `post-rewrite`)
- Initialize metadata tracking for the current branch

Verify the installation:

```bash
ls -la .git/hooks/post-*
python3 /path/to/claude-git-sync/src/git_sync.py status
```

### Step 3: Install the git-claude Wrapper (Recommended)

The wrapper provides a more convenient CLI experience:

```bash
cd /path/to/claude-git-sync
chmod +x install-git-wrapper.sh
./install-git-wrapper.sh
```

You'll be prompted to choose:
- **Option 1**: System-wide install to `/usr/local/bin/git-claude`
- **Option 2**: Add to your `$PATH`

Verify:

```bash
git-claude status
```

### Step 4 (Optional): Set Up an Alias

For the smoothest experience, alias `git` to `git-claude`:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias git='git-claude'
```

Now all your normal `git` commands will automatically sync chat sessions.

---

## Configuration

### View Current Configuration

```bash
git-claude config
# or
python3 src/git_sync.py config
```

### Available Settings

| Setting                      | Default  | Description                              |
|------------------------------|----------|------------------------------------------|
| `merge.strategy`             | `append` | How to merge chats: `append`, `keep`, `replace` |
| `merge.autoBackup`           | `true`   | Auto-backup before merging               |
| `archive.enabled`            | `false`  | Auto-archive old branches                |
| `archive.maxBranchAgeDays`   | `90`     | Days before archiving                    |
| `compression.enabled`        | `false`  | Auto-compress large sessions             |
| `compression.threshold`      | `1000`   | Compress after N messages                |
| `search.indexEnabled`        | `false`  | Build search index for faster queries    |
| `output.verbose`             | `false`  | Verbose output                           |
| `output.useColor`            | `true`   | Colored terminal output                  |
| `output.pageSize`            | `20`     | Messages per page in history             |
| `history.showTimestamps`     | `true`   | Show timestamps in timeline              |
| `history.maxPreviewLength`   | `100`    | Preview length in timeline               |

### Set Configuration Values

```bash
# Enable compression for large sessions
git-claude config set compression.enabled true

# Set merge strategy
git-claude config set merge.strategy append

# Enable auto-archiving
git-claude config set archive.enabled true
git-claude config set archive.maxBranchAgeDays 60

# Reset to defaults
git-claude config reset
```

---

## Basic Usage

### Automatic Mode (Just Use Git Normally)

Once hooks are installed, everything happens automatically:

```bash
# Switch branch -> chat context switches too
git checkout feature-login

# Create a new branch -> inherits parent chat context
git checkout -b feature-oauth

# Commit -> chat state is saved
git commit -m "Add OAuth flow"

# Merge -> chat histories are merged
git merge feature-login

# Rebase -> chat backup is created automatically
git rebase main
```

### Manual Commands

```bash
# Save the current chat session
python3 src/git_sync.py save

# Switch chat to a specific branch
python3 src/git_sync.py switch feature-auth

# Create a new branch with inherited chat
python3 src/git_sync.py create feature-new main

# Check sync status
python3 src/git_sync.py status
```

---

## Advanced Usage

### History & Timeline

```bash
# View chat timeline for current branch
git-claude history

# View timeline for a specific branch, limited to 10 messages
git-claude history main --limit 10

# View with offset (pagination)
git-claude history main --limit 20 --offset 40
```

### Search

```bash
# Search for a keyword across all branches
git-claude search "authentication"

# Search with regex
git-claude search "auth.*token" --regex

# Search in a specific branch
git-claude search "login" --branch feature-auth

# Show context around matches
git-claude search "bug fix" -C 3
```

### Branch Comparison

```bash
# Compare chat histories between two branches
git-claude diff-branches main feature-auth

# View statistics for a branch
git-claude stats feature-auth

# View overall statistics
git-claude stats
```

### Stash Support

Save and restore chat context alongside Git stashes:

```bash
# Stash code AND chat context
git stash
git-claude stash-save "work-in-progress auth"

# List chat stashes
git-claude stash-list

# Restore code AND chat
git stash pop
git-claude stash-restore
```

### Tag Snapshots

Save chat state at release milestones:

```bash
# Save snapshot at a release tag
git-claude tag v1.0.0 "Production release with auth system"

# List all tag snapshots
git-claude tag-list

# Restore chat from a tag
git-claude tag-restore v1.0.0

# Delete a tag snapshot
git-claude tag-delete v1.0.0
```

### Storage Management

```bash
# View storage statistics
git-claude storage

# Quick optimization (compress large sessions)
git-claude vacuum

# Full optimization (compress + deduplicate + clean temp files)
git-claude vacuum --full
```

### Branch Cleanup

```bash
# Find orphaned branches (branches deleted from Git but still have chat data)
git-claude cleanup

# Auto-archive orphaned branches
git-claude cleanup --archive

# List archived branches
git-claude list-archived

# Remove archived branches older than 30 days
git-claude prune --days 30

# Dry run first to see what would be removed
git-claude prune --days 30 --dry-run
```

### Multi-Project Management

```bash
# Register a project
git-claude project add /home/user/projects/my-app "My App"

# List all registered projects
git-claude projects

# Show project details
git-claude project info "My App"

# Unregister a project
git-claude project remove "My App"
```

### Merge Conflict Helper

When you encounter a Git merge conflict, get relevant chat context:

```bash
# Show conflict resolution help with relevant chat history
git-claude conflicts
```

This scans conflicting files, searches your chat history for relevant discussions, and displays them ranked by relevance.

---

## VS Code Extension

### Install

```bash
cd vscode-extension
npm install
npm run compile
npm run package
code --install-extension claude-git-sync-1.0.0.vsix
```

### Features

- **Branch Tree View** - See all branches with chat sessions in the SCM panel
- **Status Bar** - Shows current branch sync status (click to sync)
- **History Panel** - WebView panel showing chat timeline
- **Conflict Helper** - Visual conflict resolution with chat context
- **Auto-Sync** - Automatically syncs when you switch branches in VS Code

### Development Mode

Press `F5` in VS Code to launch the extension in a debug window.

### Extension Commands

Open the Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) and search for:

| Command                           | Description                        |
|-----------------------------------|------------------------------------|
| `Claude Git Sync: Sync Current`   | Manually sync current branch       |
| `Claude Git Sync: Switch Branch`  | Switch to another branch's chat    |
| `Claude Git Sync: Show History`   | Open history viewer panel          |
| `Claude Git Sync: Show Conflicts` | Open conflict helper panel         |
| `Claude Git Sync: Vacuum`         | Run storage optimization           |

---

## Real-World Workflows

### Workflow 1: Feature Development

```bash
# Start a new feature from main
git checkout main
git checkout -b feature-user-profiles

# Work with Claude Code on the feature...
# (all conversations are tracked automatically)

# Save progress and switch to fix a bug
git commit -m "WIP: user profiles"
git checkout -b hotfix-login-crash main

# Claude now has fresh context from main, not your feature work
# Fix the bug with Claude...

git commit -m "Fix login crash"
git checkout main
git merge hotfix-login-crash

# Go back to your feature - Claude remembers your feature discussion!
git checkout feature-user-profiles
```

### Workflow 2: Code Review with History

```bash
# Reviewer checks out the PR branch
git checkout feature-user-profiles

# See what Claude helped with
git-claude history feature-user-profiles

# Search for specific discussions
git-claude search "security" --branch feature-user-profiles

# Compare with main branch context
git-claude diff-branches main feature-user-profiles
```

### Workflow 3: Release Tagging

```bash
# Prepare release
git checkout main
git merge feature-user-profiles

# Tag the release and save chat snapshot
git tag v2.0.0
git-claude tag v2.0.0 "User profiles release"

# Later, if you need to debug v2.0.0
git-claude tag-restore v2.0.0
# Now you have the exact chat context from release time
```

### Workflow 4: Team Collaboration with Stash

```bash
# You're mid-conversation with Claude about a complex refactor
# Teammate needs urgent help on their branch

# Save everything
git stash
git-claude stash-save "refactor discussion"

# Help teammate
git checkout teammate-branch
# ... work with Claude on their issue ...

# Come back to your work
git checkout your-branch
git stash pop
git-claude stash-restore
# Claude remembers exactly where you left off
```

---

## Command Reference

### Core Commands

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `save`                            | Save current chat session                      |
| `switch <branch>`                 | Switch to a branch's chat                      |
| `create <branch> [base]`         | Create branch with inherited chat              |
| `status`                          | Show sync status                               |
| `auto`                            | Auto-handler (used by Git hooks)               |
| `help`                            | Show help text                                 |

### Merge & Conflict

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `merge <source-branch>`          | Merge chat from source branch                  |
| `conflicts`                       | Show merge conflict resolution help            |

### History & Search

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `history [branch] [--limit N]`   | Show chat timeline                             |
| `search <pattern> [--regex]`     | Search messages                                |
| `diff-branches <b1> <b2>`       | Compare two branches                           |
| `stats [branch]`                 | Show statistics                                |

### Stash

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `stash-save [name]`              | Save chat context with stash                   |
| `stash-restore [ref]`            | Restore chat from stash                        |
| `stash-list`                      | List stash contexts                            |

### Tags

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `tag <name> [description]`       | Save session snapshot                          |
| `tag-restore <name>`             | Restore from snapshot                          |
| `tag-list`                        | List all snapshots                             |
| `tag-delete <name>`              | Delete a snapshot                              |

### Storage & Cleanup

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `vacuum [--full]`                | Optimize storage                               |
| `storage`                         | Show storage statistics                        |
| `cleanup [--archive]`            | Find/archive orphaned branches                 |
| `prune [--days N] [--dry-run]`   | Remove old archives                            |
| `list-archived`                   | List archived branches                         |

### Configuration

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `config`                          | Show all settings                              |
| `config get <key>`               | Get a setting                                  |
| `config set <key> <value>`       | Set a setting                                  |
| `config reset`                    | Reset to defaults                              |

### Projects

| Command                           | Description                                    |
|-----------------------------------|------------------------------------------------|
| `projects`                        | List registered projects                       |
| `project add <path> [name]`      | Register a project                             |
| `project remove <name>`          | Unregister a project                           |
| `project info <name>`            | Show project details                           |

---

## Troubleshooting

### Hooks Not Triggering

```bash
# Check hooks exist and are executable
ls -la .git/hooks/post-*

# Re-install hooks
python3 /path/to/claude-git-sync/src/setup_integration.py

# Make hooks executable manually
chmod +x .git/hooks/post-checkout
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/post-merge
chmod +x .git/hooks/post-rewrite
```

### Python Not Found

```bash
# Check Python path
which python3

# If using a different path, update the shebang in hooks:
# Change #!/usr/bin/env python3 to your python path
```

### Chat Not Switching on Branch Change

```bash
# Test the hook manually
python3 /path/to/claude-git-sync/src/git_sync.py auto

# Check if .claude-git-sync/ directory exists
ls -la .claude-git-sync/

# Check metadata
cat .claude-git-sync/metadata.json
```

### Storage Growing Too Large

```bash
# Check current storage usage
git-claude storage

# Run full optimization
git-claude vacuum --full

# Enable auto-compression
git-claude config set compression.enabled true
git-claude config set compression.threshold 500

# Archive old branches
git-claude cleanup --archive
git-claude prune --days 30
```

### VS Code Extension Not Working

```bash
# Verify the extension is installed
code --list-extensions | grep claude

# Check the Python path setting
# In VS Code settings: "claudeGitSync.pythonPath": "python3"

# Reload VS Code window
# Ctrl+Shift+P -> "Developer: Reload Window"

# Check extension logs
# View -> Output -> select "Claude Git Sync" from dropdown
```

### Permission Errors

```bash
# Fix hook permissions
chmod +x .git/hooks/post-*

# Fix sync directory permissions
chmod -R u+rw .claude-git-sync/
```

---

## Data Storage

All data is stored locally in your project under `.claude-git-sync/`:

```
.claude-git-sync/
├── sessions/              # Active branch sessions (.jsonl or .jsonl.gz)
├── archived-sessions/     # Archived old branch sessions
├── rebase-backups/        # Pre-rebase safety backups
├── stashes/               # Stash chat contexts
├── tags/                  # Tag snapshots
├── config.json            # Local configuration overrides
└── metadata.json          # Branch tracking and sync state
```

Add `.claude-git-sync/` to your `.gitignore` to keep chat data local:

```bash
echo ".claude-git-sync/" >> .gitignore
```
