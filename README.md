# Claude Git Sync

Automatically sync Claude Code chat sessions with Git branches. Each branch gets its own chat history with intelligent merging, search, and conflict resolution.

## Features

### Core
- 🔄 **Auto Branch Sync** - Chat automatically switches with Git branches
- 🌳 **Hierarchical Inheritance** - Child branches inherit parent context
- 🔀 **Smart Merging** - Merge chat histories with configurable strategies
- 💾 **Stash Support** - Save/restore chat with Git stashes

### Advanced
- ⚙️ **Configuration** - Global and local settings
- 🗜️ **Optimization** - 93% compression, deduplication, indexing
- 🔄 **Rebase Support** - Automatic backups
- 🏷️ **Tag Snapshots** - Save/restore at release points
- 🔍 **History & Search** - Timeline viewer, full-text search
- 🔥 **Conflict Helper** - Context during merge conflicts
- 📁 **Multi-Project** - Manage multiple repositories
- 🎨 **VS Code Extension** - Full IDE integration

## Quick Start

```bash
git clone https://github.com/yourusername/claude-git-sync.git
cd claude-git-sync
python3 src/setup_integration.py
```

Optional wrapper for better CLI experience:
```bash
./install-git-wrapper.sh
```

## Usage

### Automatic (Recommended)
Just use Git normally - hooks handle everything:
```bash
git checkout feature-auth   # → Chat switches automatically
git commit -m "Add login"   # → Chat saves automatically
git merge feature-payments  # → Chats merge automatically
```

### Manual Commands
```bash
python3 src/git_sync.py save     # Save current chat
python3 src/git_sync.py status   # Show sync status
python3 src/git_sync.py help     # Full command list
```

### With git-claude Wrapper
```bash
git-claude history               # View timeline
git-claude search "auth"         # Search messages
git-claude conflicts             # Conflict help
git-claude vacuum --full         # Optimize storage
git-claude stats                 # Statistics
```

## Key Commands

```bash
# Configuration
git-claude config                        # Show all settings
git-claude config set merge.strategy append

# History & Search
git-claude history main --limit 20       # Timeline
git-claude search "pattern" --regex      # Search
git-claude diff-branches main feature    # Compare
git-claude stats                         # Statistics

# Storage
git-claude storage                       # Usage stats
git-claude vacuum                        # Compress
git-claude vacuum --full                 # Full optimization

# Tags
git-claude tag v1.0 "Release"           # Save snapshot
git-claude tag-list                      # List snapshots
git-claude tag-restore v1.0              # Restore

# Cleanup
git-claude cleanup --archive             # Archive orphaned
git-claude list-archived                 # List archives
git-claude prune --days 30               # Remove old

# Projects
git-claude projects                      # List all
git-claude project add /path/to/repo     # Register

# Conflicts
git-claude conflicts                     # Show help
```

## How It Works

1. **Git Hooks** - Trigger on checkout, commit, merge, rebase
2. **Session Storage** - Backups in `.claude-git-sync/sessions/`
3. **Metadata Tracking** - Branch info in `metadata.json`
4. **Compression** - Auto-compress old/large sessions
5. **Inheritance** - Child branches inherit parent chat

## Directory Structure

```
.claude-git-sync/
├── sessions/           # Branch sessions (.jsonl, .jsonl.gz)
├── archived-sessions/  # Archived branches
├── rebase-backups/     # Pre-rebase backups
├── tags/              # Tag snapshots
├── config.json        # Local configuration
└── metadata.json      # Branch tracking
```

## Configuration

```bash
# Enable compression
git-claude config set compression.enabled true

# Set merge strategy (append/keep/replace)
git-claude config set merge.strategy append

# Archive old branches
git-claude config set archive.enabled true
git-claude config set archive.maxBranchAgeDays 90
```

## VS Code Extension

Full IDE integration with:
- Branch tree view in SCM panel
- Clickable status bar indicator
- WebView panels for history/conflicts
- Auto-sync on branch changes

**Install:**
```bash
cd vscode-extension
npm install && npm run compile
code --install-extension $(npm run package | grep -o '.*\.vsix')
```

## Documentation

- [INSTALL.md](INSTALL.md) - Detailed installation
- [MERGE-GUIDE.md](MERGE-GUIDE.md) - Merge strategies
- [STASH-GUIDE.md](STASH-GUIDE.md) - Stash workflows

## Requirements

- Python 3.7+
- Git 2.0+
- Claude Code CLI
- VS Code 1.80+ (for extension)

## Troubleshooting

**Not syncing?**
```bash
python3 src/git_sync.py status
ls -la .git/hooks/post-*
```

**Large storage?**
```bash
git-claude vacuum --full
```

## License

MIT

## Contributing

Issues and PRs welcome!
