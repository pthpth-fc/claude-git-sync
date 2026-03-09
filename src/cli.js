#!/usr/bin/env node
import { BranchManager } from './branch-manager.js';

/**
 * CLI interface for Claude-Git sync
 */

const command = process.argv[2];
const args = process.argv.slice(3);

const manager = new BranchManager();

try {
  switch (command) {
    case 'init':
      const branch = args[0] || manager.storage.getCurrentBranch();
      const parent = args[1] || null;
      manager.initBranch(branch, parent);
      break;

    case 'switch':
      if (!args[0]) {
        console.error('Usage: claude-git-sync switch <branch>');
        process.exit(1);
      }
      manager.switchToBranch(args[0]);
      break;

    case 'save':
      // This would be called by Claude Code to save chat state
      // For now, just create a placeholder
      console.log('Save command - to be integrated with Claude Code');
      break;

    case 'create':
      if (!args[0]) {
        console.error('Usage: claude-git-sync create <new-branch> [base-branch]');
        process.exit(1);
      }
      manager.createBranch(args[0], args[1]);
      break;

    case 'status':
      const status = manager.getStatus();
      console.log('\n📊 Claude-Git Sync Status');
      console.log('─'.repeat(50));
      console.log(`Current Branch: ${status.currentBranch}`);
      console.log(`Current Chat ID: ${status.currentChatId || 'none'}`);
      console.log(`Total Tracked Branches: ${status.totalBranches}`);
      console.log('\nBranch Mappings:');
      for (const [branch, chatId] of Object.entries(status.mappings)) {
        const indicator = branch === status.currentBranch ? '→' : ' ';
        console.log(`${indicator} ${branch}: ${chatId}`);
      }
      break;

    case 'help':
    default:
      console.log(`
Claude-Git Sync - Sync chat sessions with Git branches

Usage:
  claude-git-sync <command> [arguments]

Commands:
  init [branch] [parent]    Initialize chat session for branch
  switch <branch>           Switch to branch's chat session
  create <branch> [base]    Create new branch with chat session
  save                      Save current chat state
  status                    Show sync status
  help                      Show this help

Examples:
  claude-git-sync init                    # Init current branch
  claude-git-sync switch feature-auth     # Switch to feature-auth chat
  claude-git-sync create feature-new      # Create branch with chat
  claude-git-sync status                  # Show status
      `);
  }
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
