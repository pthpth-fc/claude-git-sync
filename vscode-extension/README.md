# Claude Git Sync - VS Code Extension

Integrates Claude Git Sync with Visual Studio Code for seamless chat session management.

## Features

- **Branch Tree View**: View all branches with message counts in the SCM panel
- **Status Bar**: Shows current branch and message count (clickable to view history)
- **Commands**: Access all Claude Git Sync features from the command palette
- **History Viewer**: View chat history in a WebView panel
- **Conflict Helper**: Get chat context during merge conflicts

## Installation

### From Source (Local Installation)

1. Install dependencies:
   ```bash
   cd vscode-extension
   npm install
   ```

2. Compile TypeScript:
   ```bash
   npm run compile
   ```

3. Install the extension:
   - Press F5 in VS Code to launch Extension Development Host
   - Or package and install manually:
     ```bash
     npm run package
     code --install-extension claude-git-sync-1.0.0.vsix
     ```

## Usage

1. Open a repository with Claude Git Sync installed
2. The extension activates automatically
3. View branches in the SCM panel under "Claude Chat Sessions"
4. Click the status bar indicator to view history
5. Use Command Palette (Ctrl+Shift+P) for all commands:
   - `Claude Git Sync: Save Current Session`
   - `Claude Git Sync: Show History`
   - `Claude Git Sync: Show Conflicts`
   - `Claude Git Sync: Optimize Storage`

## Configuration

Set these in VS Code settings:

- `claudeGitSync.pythonPath`: Path to Python 3 (default: "python3")
- `claudeGitSync.autoSync`: Auto-sync on branch changes (default: true)
- `claudeGitSync.showStatusBar`: Show status bar indicator (default: true)
- `claudeGitSync.conflictHelperEnabled`: Enable conflict helper (default: true)

## Requirements

- Visual Studio Code 1.80.0 or higher
- Python 3.7+
- Claude Git Sync installed in the repository

## Development

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Package extension
npm run package
```

## License

MIT
