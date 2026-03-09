# Installation Guide

## Prerequisites

- Python 3.7+
- Git 2.0+
- Claude Code CLI
- Git repository

## Basic Installation

```bash
# 1. Clone
git clone https://github.com/yourusername/claude-git-sync.git
cd claude-git-sync

# 2. Install hooks
python3 src/setup_integration.py
```

This creates:
- `.claude-git-sync/` directory
- Git hooks (post-checkout, post-commit, post-merge, post-rewrite)
- Metadata tracking

## Optional: git-claude Wrapper

```bash
chmod +x install-git-wrapper.sh
./install-git-wrapper.sh
```

Choose option 1 (system-wide) or 2 (PATH).

## Verification

```bash
# Check hooks
ls -la .git/hooks/post-*

# Test sync
python3 src/git_sync.py status

# Test wrapper (if installed)
git-claude status
```

## VS Code Extension

```bash
cd vscode-extension
npm install
npm run compile
npm run package
code --install-extension claude-git-sync-1.0.0.vsix
```

Or press F5 for development mode.

## Configuration

```bash
# Enable features
git-claude config set compression.enabled true
git-claude config set archive.enabled true

# Set merge strategy
git-claude config set merge.strategy append
```

## Troubleshooting

**Hooks not working:**
```bash
chmod +x .git/hooks/post-*
python3 src/setup_integration.py
```

**Python path issues:**
```bash
which python3
# Update shebang if needed
```

**VS Code extension:**
```bash
# Check settings
"claudeGitSync.pythonPath": "python3"

# Reload window
Ctrl+Shift+P → "Reload Window"
```

## Uninstall

```bash
# Remove hooks
rm .git/hooks/post-checkout
rm .git/hooks/post-commit
rm .git/hooks/post-merge
rm .git/hooks/post-rewrite

# Remove data (optional)
rm -rf .claude-git-sync/

# Remove wrapper
sudo rm /usr/local/bin/git-claude
```

## Next Steps

- [README.md](README.md) - All features
- [MERGE-GUIDE.md](MERGE-GUIDE.md) - Merge strategies
- [STASH-GUIDE.md](STASH-GUIDE.md) - Stash workflows
