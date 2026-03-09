# Quick Start Guide

Get Claude-Git Sync running in 5 minutes!

## Step 1: Install (30 seconds)

```bash
cd ~/Desktop/claude-git-sync
node src/setup.js
```

This installs Git hooks and initializes your current branch.

## Step 2: Configure Claude Code (2 minutes)

### Option A: Via Settings File

Edit `~/.config/claude-code/settings.json`:

```json
{
  "hooks": {
    "onSessionStart": "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-session-start.sh",
    "onToolCall": "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-tool-call.sh",
    "onUserPromptSubmit": "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-prompt.sh"
  }
}
```

### Option B: Via CLI (if available)

```bash
claude-code config set hooks.onSessionStart "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-session-start.sh"
claude-code config set hooks.onToolCall "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-tool-call.sh"
claude-code config set hooks.onUserPromptSubmit "bash /home/pth/Desktop/claude-git-sync/hooks/claude-on-prompt.sh"
```

## Step 3: Test It! (2 minutes)

```bash
# Check status
node src/cli.js status

# Create a new feature branch with chat context
node src/cli.js create feature-test

# Switch back to main
git checkout master
# Notice: Chat context automatically switches!

# Return to feature
git checkout feature-test
# Notice: Chat context restored!
```

## Step 4: Use It Daily

### Create New Feature
```bash
node src/cli.js create feature-my-awesome-feature
# Git branch created + chat session initialized
```

### Normal Git Workflow
```bash
git checkout feature-auth
# Chat automatically loads for this branch

# Work with Claude Code...
# Chat state auto-saves

git checkout main
# Chat switches to main branch context
```

### Check What's Going On
```bash
node src/cli.js status
```

## How to Know It's Working

You should see these messages:

**When switching branches:**
```
🔄 Branch switched to: feature-auth
📝 Loading chat session...

📝 Switched to chat session for branch: feature-auth
   Chat ID: feature-auth-1234567890
   Inheritance: main → feature-auth
```

**When starting Claude Code:**
```
╔════════════════════════════════════════════════════════╗
║         Claude-Git Sync Active                        ║
╚════════════════════════════════════════════════════════╝

Current branch: feature-auth
```

## Troubleshooting

**Not seeing messages?**
- Run `node src/cli.js status` to verify setup
- Check that hooks are executable: `ls -la hooks/`
- Test Git hook manually: `bash .git/hooks/post-checkout`

**Claude Code hooks not working?**
- Verify settings file location
- Check Claude Code documentation for hook configuration
- Test hooks manually: `bash hooks/claude-on-session-start.sh`

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Run the demo: `bash demo.sh`
- Start working on your project with branch-synced chats!

## Pro Tips

1. **Use descriptive branch names** - they'll appear in your chat history
2. **Create branches for experiments** - each gets isolated chat context
3. **Check status often** - `node src/cli.js status` shows all mappings
4. **Commit regularly** - triggers auto-save of chat state

Enjoy seamless Git + Claude Code integration! 🚀
