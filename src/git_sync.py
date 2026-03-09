#!/usr/bin/env python3
"""
Git-Claude Sync - Main Integration Script
Handles branch switching and chat session synchronization
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))

from claude_session_manager import ClaudeSessionManager


class GitClaudeSync:
    def __init__(self):
        try:
            self.manager = ClaudeSessionManager()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def sync_current_branch(self):
        """Save current branch's chat session"""
        branch = self.manager.get_current_branch()
        print(f"💾 Saving chat session for branch: {branch}")
        success = self.manager.backup_current_session(branch)

        if success:
            print(f"✓ Session saved successfully")
        else:
            print(f"⚠️  Could not save session (this is OK if no active chat)")

        return success

    def switch_to_branch(self, target_branch: str):
        """Switch to a branch and load its chat session"""
        current_branch = self.manager.get_current_branch()

        # Save current branch first
        print(f"📝 Saving current branch: {current_branch}")
        self.manager.backup_current_session(current_branch)

        print()
        print(f"🔄 Switching to branch: {target_branch}")
        print()

        # Check if target branch has a session
        branch_info = self.manager.get_branch_info(target_branch)

        if branch_info:
            print(f"📚 Branch '{target_branch}' has existing chat history")
            print(f"   Messages: {branch_info.get('messageCount', 0)}")
            if 'inheritedFrom' in branch_info:
                print(f"   Inherited from: {branch_info['inheritedFrom']}")

            # Restore session
            success = self.manager.restore_branch_session(target_branch)

            if success:
                print()
                print(f"✅ Restored chat session for branch: {target_branch}")
            else:
                print()
                print(f"⚠️  Could not restore session")
        else:
            print(f"🆕 No existing chat for branch '{target_branch}'")
            print(f"   Starting fresh session")

            # Initialize new branch
            self.manager.initialize_branch(target_branch, current_branch)

        print()
        print("─" * 60)
        print(f"Ready to chat on branch: {target_branch}")
        print("─" * 60)

    def create_branch_with_chat(self, new_branch: str, base_branch: Optional[str] = None):
        """Create new Git branch with inherited chat context"""
        current_branch = self.manager.get_current_branch()
        base = base_branch or current_branch

        try:
            # Create Git branch
            print(f"🌿 Creating branch '{new_branch}' from '{base}'...")
            subprocess.run(
                ['git', 'checkout', '-b', new_branch, base],
                check=True,
                cwd=self.manager.repo_root
            )

            # Initialize with parent context
            print()
            parent_info = self.manager.get_branch_info(base)
            if parent_info:
                print(f"📚 Inheriting chat context from '{base}'")
                print(f"   Parent has {parent_info.get('messageCount', 0)} messages")

            self.manager.initialize_branch(new_branch, base)

            print()
            print(f"✅ Branch '{new_branch}' created with chat session!")

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create branch: {e}")
            sys.exit(1)

    def show_status(self):
        """Show current sync status"""
        current_branch = self.manager.get_current_branch()
        branches = self.manager.list_branches()
        stashes = self.manager.list_stashes()

        print()
        print("╔════════════════════════════════════════════════════════╗")
        print("║         Claude-Git Sync Status                        ║")
        print("╚════════════════════════════════════════════════════════╝")
        print()
        print(f"📍 Current Branch: {current_branch}")

        current_info = branches.get(current_branch)
        if current_info:
            print(f"   Messages: {current_info.get('messageCount', 0)}")
            if 'inheritedFrom' in current_info:
                print(f"   Inherited from: {current_info['inheritedFrom']}")
        else:
            print(f"   No session saved yet")

        print()
        print(f"📊 Total Tracked Branches: {len(branches)}")

        if branches:
            print()
            print("Branch Sessions:")
            print("─" * 60)

            for branch, info in sorted(branches.items()):
                indicator = "→" if branch == current_branch else " "
                msg_count = info.get('messageCount', 0)
                parent = info.get('inheritedFrom', info.get('parentBranch', ''))

                print(f"{indicator} {branch}")
                print(f"   Messages: {msg_count}")
                if parent:
                    print(f"   Parent: {parent}")
                print()

        if stashes:
            print("💾 Saved Stashes:")
            print("─" * 60)
            for stash_ref, info in sorted(stashes.items(),
                                         key=lambda x: x[1].get('created', ''),
                                         reverse=True):
                print(f"  {stash_ref}")
                print(f"   Branch: {info.get('branch', 'unknown')}")
                print(f"   Messages: {info.get('messageCount', 0)}")
                print(f"   Created: {info.get('created', 'unknown')[:19]}")
                print()

        print("─" * 60)
        print()

    def save_stash(self, stash_name: Optional[str] = None):
        """Save chat context for a stash"""
        print("💾 Saving chat context for stash...")
        success = self.manager.save_stash_context(stash_name)
        if success:
            print("✓ Chat context saved with stash")
        else:
            print("⚠️  Could not save stash context")

    def restore_stash(self, stash_ref: Optional[str] = None):
        """Restore chat context from a stash"""
        print("📚 Restoring chat context from stash...")
        success = self.manager.restore_stash_context(stash_ref)
        if not success:
            print("⚠️  Could not restore stash context")

    def list_stashes(self):
        """List all stash contexts"""
        stashes = self.manager.list_stashes()

        if not stashes:
            print("No stash contexts saved")
            return

        print()
        print("💾 Saved Stash Contexts")
        print("─" * 60)

        for stash_ref, info in sorted(stashes.items(),
                                     key=lambda x: x[1].get('created', ''),
                                     reverse=True):
            print(f"📦 {stash_ref}")
            print(f"   Branch: {info.get('branch', 'unknown')}")
            print(f"   Messages: {info.get('messageCount', 0)}")
            print(f"   Created: {info.get('created', 'unknown')}")
            print()
        print("─" * 60)

    def auto_switch_handler(self):
        """Automatic handler for Git post-checkout hook"""
        target_branch = self.manager.get_current_branch()
        metadata = self.manager.load_metadata()
        last_branch = metadata.get('currentBranch')

        # Only act if branch actually changed
        if last_branch and last_branch != target_branch:
            print()
            print("🔄 Branch switch detected!")
            print(f"   {last_branch} → {target_branch}")
            print()

            self.switch_to_branch(target_branch)
        else:
            # First time or same branch - just save
            self.sync_current_branch()


def main():
    if len(sys.argv) < 2:
        command = 'help'
        args = []
    else:
        command = sys.argv[1]
        args = sys.argv[2:]

    sync = GitClaudeSync()

    try:
        if command == 'save':
            sync.sync_current_branch()

        elif command == 'switch':
            if not args:
                print('Usage: git-sync switch <branch>')
                sys.exit(1)
            sync.switch_to_branch(args[0])

        elif command == 'create':
            if not args:
                print('Usage: git-sync create <new-branch> [base-branch]')
                sys.exit(1)
            base = args[1] if len(args) > 1 else None
            sync.create_branch_with_chat(args[0], base)

        elif command == 'status':
            sync.show_status()

        elif command == 'auto':
            # Called by Git hook
            sync.auto_switch_handler()

        elif command == 'stash-save':
            stash_name = args[0] if args else None
            sync.save_stash(stash_name)

        elif command == 'stash-restore':
            stash_ref = args[0] if args else None
            sync.restore_stash(stash_ref)

        elif command == 'stash-list':
            sync.list_stashes()

        elif command == 'help':
            print('''
╔════════════════════════════════════════════════════════╗
║   Claude-Git Sync - Branch-Aware Chat Sessions        ║
╚════════════════════════════════════════════════════════╝

Automatically sync Claude Code chat sessions with Git branches.
Each branch gets its own chat history with hierarchical inheritance.

Commands:
  save                      Save current chat session
  switch <branch>           Manually switch to branch's chat
  create <branch> [base]    Create new branch with inherited chat
  status                    Show sync status and branch info
  auto                      Auto-handler (used by Git hooks)
  stash-save [name]         Save chat context with stash
  stash-restore [ref]       Restore chat context from stash
  stash-list                List all stash contexts
  help                      Show this help

Examples:
  python3 src/git_sync.py save
  python3 src/git_sync.py switch feature-auth
  python3 src/git_sync.py create feature-new
  python3 src/git_sync.py status
  python3 src/git_sync.py stash-save "my-work"
  python3 src/git_sync.py stash-restore
  python3 src/git_sync.py stash-list

How It Works:
  1. Each Git branch has its own Claude Code chat session
  2. Switching branches automatically saves/loads chat history
  3. New branches inherit chat context from parent branch
  4. Full conversation history backed up per branch

Setup:
  Run 'python3 src/setup_integration.py' to install Git hooks
            ''')

        else:
            print(f'Unknown command: {command}')
            print('Run "python3 src/git_sync.py help" for usage')
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
