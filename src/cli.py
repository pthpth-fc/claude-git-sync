#!/usr/bin/env python3
"""
CLI interface for Claude-Git sync
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from branch_manager import BranchManager


def main():
    if len(sys.argv) < 2:
        command = 'help'
        args = []
    else:
        command = sys.argv[1]
        args = sys.argv[2:]

    manager = BranchManager()

    try:
        if command == 'init':
            branch = args[0] if args else manager.storage.get_current_branch()
            parent = args[1] if len(args) > 1 else None
            manager.init_branch(branch, parent)

        elif command == 'switch':
            if not args:
                print('Usage: claude-git-sync switch <branch>')
                sys.exit(1)
            manager.switch_to_branch(args[0])

        elif command == 'save':
            # This would be called by Claude Code to save chat state
            print('Save command - to be integrated with Claude Code')

        elif command == 'create':
            if not args:
                print('Usage: claude-git-sync create <new-branch> [base-branch]')
                sys.exit(1)
            base = args[1] if len(args) > 1 else None
            manager.create_branch(args[0], base)

        elif command == 'status':
            status = manager.get_status()
            print('\n📊 Claude-Git Sync Status')
            print('─' * 50)
            print(f'Current Branch: {status["currentBranch"]}')
            print(f'Current Chat ID: {status["currentChatId"] or "none"}')
            print(f'Total Tracked Branches: {status["totalBranches"]}')
            print('\nBranch Mappings:')
            for branch, chat_id in status['mappings'].items():
                indicator = '→' if branch == status['currentBranch'] else ' '
                print(f'{indicator} {branch}: {chat_id}')

        elif command == 'help':
            print('''
Claude-Git Sync - Sync chat sessions with Git branches

Usage:
  python3 src/cli.py <command> [arguments]

Commands:
  init [branch] [parent]    Initialize chat session for branch
  switch <branch>           Switch to branch's chat session
  create <branch> [base]    Create new branch with chat session
  save                      Save current chat state
  status                    Show sync status
  help                      Show this help

Examples:
  python3 src/cli.py init                    # Init current branch
  python3 src/cli.py switch feature-auth     # Switch to feature-auth chat
  python3 src/cli.py create feature-new      # Create branch with chat
  python3 src/cli.py status                  # Show status
            ''')

        else:
            print(f'Unknown command: {command}')
            print('Run "python3 src/cli.py help" for usage')
            sys.exit(1)

    except Exception as e:
        print(f'Error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
