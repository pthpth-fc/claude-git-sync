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
from merge_manager import MergeManager
from history_viewer import HistoryViewer
from conflict_helper import ConflictHelper
from project_manager import ProjectManager


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

        elif command == 'merge':
            if not args:
                print('Usage: git-sync merge <source-branch>')
                sys.exit(1)
            merger = MergeManager()
            merger.auto_merge(args[0])

        elif command == 'config':
            if not args:
                # Show all configuration
                sync.manager.config.display()
            elif args[0] == 'get':
                if len(args) < 2:
                    print('Usage: git-sync config get <key>')
                    sys.exit(1)
                value = sync.manager.config.get(args[1])
                if value is not None:
                    print(f"{args[1]}: {value}")
                else:
                    print(f"Configuration key '{args[1]}' not found")
                    sys.exit(1)
            elif args[0] == 'set':
                if len(args) < 3:
                    print('Usage: git-sync config set <key> <value>')
                    sys.exit(1)
                # Parse value (handle boolean and numeric types)
                value = args[2]
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit():
                    value = float(value)

                if sync.manager.config.set(args[1], value):
                    print(f"Configuration updated: {args[1]} = {value}")
                else:
                    print(f"Failed to update configuration")
                    sys.exit(1)
            elif args[0] == 'reset':
                if sync.manager.config.reset():
                    print("Configuration reset to defaults")
                else:
                    print("Failed to reset configuration")
                    sys.exit(1)
            else:
                print(f"Unknown config subcommand: {args[0]}")
                print("Usage: config [get <key> | set <key> <value> | reset]")
                sys.exit(1)

        elif command == 'projects':
            # List all registered projects
            pm = ProjectManager()
            pm.display_projects()

        elif command == 'project':
            if not args:
                print('Usage: git-sync project <add|remove|info> [args]')
                sys.exit(1)

            subcommand = args[0]
            pm = ProjectManager()

            if subcommand == 'add':
                if len(args) < 2:
                    print('Usage: git-sync project add <path> [name]')
                    sys.exit(1)
                repo_path = args[1]
                name = args[2] if len(args) > 2 else None
                pm.register_project(repo_path, name)

            elif subcommand == 'remove':
                if len(args) < 2:
                    print('Usage: git-sync project remove <name>')
                    sys.exit(1)
                pm.unregister_project(args[1])

            elif subcommand == 'info':
                if len(args) < 2:
                    print('Usage: git-sync project info <name>')
                    sys.exit(1)
                pm.show_project_info(args[1])

            else:
                print(f"Unknown subcommand: {subcommand}")
                print("Valid subcommands: add, remove, info")
                sys.exit(1)

        elif command == 'conflicts':
            # Show conflict resolution help
            helper = ConflictHelper(sync.manager, sync.manager.storage)
            helper.display_conflict_help()

        elif command == 'history':
            # Show chat history timeline
            branch = args[0] if args else sync.manager.get_current_branch()
            limit = 20
            offset = 0

            # Parse flags
            for i, arg in enumerate(args):
                if arg == '--limit' and i + 1 < len(args):
                    try:
                        limit = int(args[i + 1])
                    except ValueError:
                        print(f"Invalid limit value: {args[i + 1]}")
                        sys.exit(1)
                elif arg == '--offset' and i + 1 < len(args):
                    try:
                        offset = int(args[i + 1])
                    except ValueError:
                        print(f"Invalid offset value: {args[i + 1]}")
                        sys.exit(1)

            viewer = HistoryViewer(sync.manager, sync.manager.storage)
            viewer.show_timeline(branch, limit=limit, offset=offset)

        elif command == 'search':
            if not args:
                print('Usage: git-sync search <pattern> [--branch <branch>] [--regex] [-C <lines>]')
                sys.exit(1)

            pattern = args[0]
            branch = None
            use_regex = '--regex' in args
            context_lines = 0

            # Parse flags
            for i, arg in enumerate(args):
                if arg == '--branch' and i + 1 < len(args):
                    branch = args[i + 1]
                elif arg == '-C' and i + 1 < len(args):
                    try:
                        context_lines = int(args[i + 1])
                    except ValueError:
                        print(f"Invalid context lines value: {args[i + 1]}")
                        sys.exit(1)

            viewer = HistoryViewer(sync.manager, sync.manager.storage)
            results = viewer.search_messages(pattern, branch, use_regex, context_lines)
            viewer.display_search_results(results, pattern)

        elif command == 'diff-branches':
            if len(args) < 2:
                print('Usage: git-sync diff-branches <branch1> <branch2>')
                sys.exit(1)

            viewer = HistoryViewer(sync.manager, sync.manager.storage)
            diff = viewer.diff_branches(args[0], args[1])
            if diff:
                viewer.display_diff(diff)

        elif command == 'stats':
            branch = args[0] if args else None
            viewer = HistoryViewer(sync.manager, sync.manager.storage)
            viewer.show_statistics(branch)

        elif command == 'tag':
            if not args:
                print('Usage: git-sync tag <tag-name> [description]')
                sys.exit(1)
            tag_name = args[0]
            description = ' '.join(args[1:]) if len(args) > 1 else None
            sync.manager.save_tag_snapshot(tag_name, description)

        elif command == 'tag-restore':
            if not args:
                print('Usage: git-sync tag-restore <tag-name>')
                sys.exit(1)
            sync.manager.restore_tag_snapshot(args[0])

        elif command == 'tag-list':
            tags = sync.manager.list_tag_snapshots()
            if not tags:
                print("No tag snapshots found")
            else:
                print(f"\n🏷️  Tag Snapshots ({len(tags)}):")
                print("=" * 60)
                for tag_name, info in tags.items():
                    created_date = datetime.fromisoformat(info['created'])
                    print(f"\n  {tag_name}")
                    print(f"    Branch: {info['branch']}")
                    print(f"    Commit: {info['commitSHA']}")
                    print(f"    Messages: {info['messageCount']}")
                    print(f"    Created: {created_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    if info.get('description'):
                        print(f"    Description: {info['description']}")
                print("\n" + "=" * 60)

        elif command == 'tag-delete':
            if not args:
                print('Usage: git-sync tag-delete <tag-name>')
                sys.exit(1)
            sync.manager.delete_tag_snapshot(args[0])

        elif command == 'cleanup':
            # Find and optionally archive orphaned branches
            archive = '--archive' in args
            orphaned = sync.manager.get_orphaned_branches()

            if not orphaned:
                print("✓ No orphaned branches found")
            else:
                print(f"Found {len(orphaned)} orphaned branch(es):")
                for branch in orphaned:
                    print(f"  - {branch}")

                if archive:
                    print("\nArchiving orphaned branches...")
                    for branch in orphaned:
                        sync.manager.archive_branch_session(branch)
                else:
                    print("\nRun with --archive flag to archive these sessions")

        elif command == 'prune':
            # Prune old archived branches
            days = 30
            dry_run = '--dry-run' in args

            # Parse --days argument
            for i, arg in enumerate(args):
                if arg == '--days' and i + 1 < len(args):
                    try:
                        days = int(args[i + 1])
                    except ValueError:
                        print(f"Invalid days value: {args[i + 1]}")
                        sys.exit(1)

            results = sync.manager.prune_old_branches(days, dry_run)

            if dry_run:
                if results['would_delete']:
                    print(f"\nWould delete {len(results['would_delete'])} archived branch(es):")
                    for item in results['would_delete']:
                        print(f"  - {item['branch']} ({item['age_days']} days old, "
                              f"{sync.manager.storage._format_bytes(item['size_bytes'])})")
                    print("\nRun without --dry-run to delete")
                else:
                    print("✓ No archived branches to delete")
            else:
                if results['deleted']:
                    print(f"✓ Deleted {len(results['deleted'])} archived branch(es)")
                    print(f"  Space freed: {sync.manager.storage._format_bytes(results['space_freed'])}")
                else:
                    print("✓ No archived branches to delete")

                if results['errors']:
                    print("\nErrors:")
                    for error in results['errors']:
                        print(f"  - {error}")

        elif command == 'list-archived':
            # List all archived branches
            archived = sync.manager.list_archived_branches()

            if not archived:
                print("No archived branches")
            else:
                print(f"\n📦 Archived Branches ({len(archived)}):")
                print("=" * 50)
                for branch, info in archived.items():
                    archive_date = datetime.fromisoformat(info['archivedDate'])
                    age_days = (datetime.now() - archive_date).days
                    archive_file = Path(info['archiveFile'])
                    size = archive_file.stat().st_size if archive_file.exists() else 0
                    print(f"\n  {branch}")
                    print(f"    Archived: {archive_date.strftime('%Y-%m-%d %H:%M:%S')} ({age_days} days ago)")
                    print(f"    Size: {sync.manager.storage._format_bytes(size)}")
                    print(f"    File: {archive_file.name}")
                print("\n" + "=" * 50)

        elif command == 'rebase-backup':
            if not args:
                print('Usage: git-sync rebase-backup <base-commit>')
                sys.exit(1)
            branch = sync.manager.get_current_branch()
            sync.manager.save_pre_rebase_backup(branch, args[0])

        elif command == 'rebase-complete':
            # Read commit mappings from stdin
            import sys as sys_module
            commit_mappings = sys_module.stdin.read()
            sync.manager.handle_rebase_complete(commit_mappings)

        elif command == 'vacuum':
            # Run comprehensive storage optimization
            if '--full' in args:
                sync.manager.storage.vacuum_complete()
            else:
                # Basic compression only
                sync.manager.storage.vacuum()

        elif command == 'storage':
            # Show storage statistics
            stats = sync.manager.storage.get_storage_stats()
            print("\n📊 Storage Statistics")
            print("=" * 50)
            print(f"Total Sessions: {stats['total_sessions']}")
            print(f"  Compressed: {stats['compressed_sessions']}")
            print(f"  Uncompressed: {stats['uncompressed_sessions']}")
            print(f"\nTotal Messages: {stats['total_messages']}")
            print(f"\nStorage Size:")
            print(f"  Total: {sync.manager.storage._format_bytes(stats['total_size_bytes'])}")
            print(f"  Compressed: {sync.manager.storage._format_bytes(stats['compressed_size_bytes'])}")
            print(f"  Uncompressed: {sync.manager.storage._format_bytes(stats['uncompressed_size_bytes'])}")
            print("=" * 50)

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
  merge <source-branch>     Merge chat context from source branch
  stash-save [name]         Save chat context with stash
  stash-restore [ref]       Restore chat context from stash
  stash-list                List all stash contexts
  projects                  List all registered projects
  project add <path> [name] Register a new project
  project remove <name>     Unregister a project
  project info <name>       Show project information
  conflicts                 Show merge conflict resolution help
  history [branch] [--limit N] [--offset N]  Show chat timeline
  search <pattern> [--branch X] [--regex] [-C N]  Search messages
  diff-branches <b1> <b2>   Compare two branches
  stats [branch]            Show statistics
  config                    Show all configuration settings
  config get <key>          Get a specific config value
  config set <key> <value>  Set a config value
  config reset              Reset configuration to defaults
  tag <name> [description]  Save session snapshot at Git tag
  tag-restore <name>        Restore session from tag snapshot
  tag-list                  List all tag snapshots
  tag-delete <name>         Delete a tag snapshot
  cleanup [--archive]       Find orphaned branches (archive if flag set)
  prune [--days N] [--dry-run]  Remove old archived branches
  list-archived             List all archived branches
  vacuum [--full]           Optimize storage (--full for complete optimization)
  storage                   Show storage statistics
  help                      Show this help

Examples:
  python3 src/git_sync.py save
  python3 src/git_sync.py switch feature-auth
  python3 src/git_sync.py create feature-new
  python3 src/git_sync.py status
  python3 src/git_sync.py merge feature-payments
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
