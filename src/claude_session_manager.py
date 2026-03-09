#!/usr/bin/env python3
"""
Claude Code Session Manager
Manages Claude Code session files (.jsonl transcripts) for branch-based chat sync
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import subprocess

from config_manager import ConfigManager
from storage_optimizer import StorageOptimizer


class ClaudeSessionManager:
    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = self.find_git_root() if not repo_root else repo_root
        self.claude_home = Path.home() / '.claude'
        self.sync_dir = Path(self.repo_root) / '.claude-git-sync'
        self.branch_sessions_dir = self.sync_dir / 'sessions'
        self.metadata_file = self.sync_dir / 'metadata.json'

        self.ensure_directories()

        # Initialize configuration manager
        self.config = ConfigManager(self.sync_dir)

        # Initialize storage optimizer
        self.storage = StorageOptimizer(self.sync_dir, self.config)

    def find_git_root(self) -> str:
        """Find Git repository root"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--show-toplevel'],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            raise Exception('Not in a Git repository')

    def ensure_directories(self):
        """Create necessary directories"""
        self.sync_dir.mkdir(exist_ok=True)
        self.branch_sessions_dir.mkdir(exist_ok=True)

        # Create additional directories for new features
        (self.sync_dir / 'archived-sessions').mkdir(exist_ok=True)
        (self.sync_dir / 'rebase-backups').mkdir(exist_ok=True)
        (self.sync_dir / 'tags').mkdir(exist_ok=True)

    def get_current_branch(self) -> str:
        """Get current Git branch"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            raise Exception('Could not determine current branch')

    def get_project_dir(self) -> Path:
        """Get Claude Code project directory for current repo"""
        # Convert /mnt/c/Users/dev to -mnt-c-Users-dev format
        project_name = self.repo_root.replace('/', '-')
        if project_name.startswith('-'):
            project_name = project_name[1:]
        project_name = '-' + project_name

        return self.claude_home / 'projects' / project_name

    def get_current_session_id(self) -> Optional[str]:
        """Get the current active session ID"""
        project_dir = self.get_project_dir()
        index_file = project_dir / 'sessions-index.json'

        if not index_file.exists():
            return None

        try:
            with open(index_file, 'r') as f:
                index_data = json.load(f)

            # Find the most recent session
            entries = index_data.get('entries', [])
            if not entries:
                return None

            # Sort by modified time, get most recent
            entries.sort(key=lambda x: x.get('modified', ''), reverse=True)
            return entries[0]['sessionId']
        except Exception as e:
            print(f"Error reading session index: {e}")
            return None

    def get_session_file(self, session_id: str) -> Optional[Path]:
        """Get path to session transcript file"""
        project_dir = self.get_project_dir()
        session_file = project_dir / f"{session_id}.jsonl"

        if session_file.exists():
            return session_file

        return None

    def get_branch_backup_file(self, branch: str) -> Path:
        """Get path to branch-specific backup file"""
        safe_branch = branch.replace('/', '-').replace(' ', '-')
        return self.branch_sessions_dir / f"{safe_branch}.jsonl"

    def load_metadata(self) -> Dict:
        """Load branch-session metadata"""
        if not self.metadata_file.exists():
            return {
                'branches': {},
                'currentBranch': None,
                'lastSync': None
            }

        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            return {'branches': {}, 'currentBranch': None}

    def save_metadata(self, metadata: Dict):
        """Save branch-session metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def backup_current_session(self, branch: str) -> bool:
        """Backup current Claude session to branch-specific file"""
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                print("No active session to backup")
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                print(f"Session file not found for {session_id}")
                return False

            # Backup to branch-specific file
            backup_file = self.get_branch_backup_file(branch)
            shutil.copy2(session_file, backup_file)

            # Count messages
            with open(backup_file, 'r') as f:
                message_count = sum(1 for line in f if line.strip())

            # Update metadata
            metadata = self.load_metadata()
            metadata['branches'][branch] = {
                'sessionId': session_id,
                'backupFile': str(backup_file),
                'messageCount': message_count,
                'lastBackup': datetime.now().isoformat()
            }
            metadata['currentBranch'] = branch
            metadata['lastSync'] = datetime.now().isoformat()
            self.save_metadata(metadata)

            print(f"✓ Backed up {message_count} messages from branch '{branch}'")
            return True

        except Exception as e:
            print(f"Error backing up session: {e}")
            return False

    def restore_branch_session(self, branch: str) -> bool:
        """Restore Claude session from branch-specific backup"""
        try:
            backup_file = self.get_branch_backup_file(branch)

            if not backup_file.exists():
                print(f"No backup found for branch '{branch}'")
                print("This branch will start with a fresh chat session")
                return False

            # Get current session info
            session_id = self.get_current_session_id()
            if not session_id:
                print("No active session to restore to")
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                print("Current session file not found")
                return False

            # Restore from backup
            shutil.copy2(backup_file, session_file)

            # Count messages
            with open(session_file, 'r') as f:
                message_count = sum(1 for line in f if line.strip())

            # Update metadata
            metadata = self.load_metadata()
            metadata['currentBranch'] = branch
            metadata['lastSync'] = datetime.now().isoformat()
            self.save_metadata(metadata)

            print(f"✓ Restored {message_count} messages for branch '{branch}'")
            return True

        except Exception as e:
            print(f"Error restoring session: {e}")
            return False

    def get_branch_info(self, branch: str) -> Optional[Dict]:
        """Get information about a branch's session"""
        metadata = self.load_metadata()
        return metadata.get('branches', {}).get(branch)

    def list_branches(self) -> Dict[str, Dict]:
        """List all branches with session data"""
        metadata = self.load_metadata()
        return metadata.get('branches', {})

    def initialize_branch(self, branch: str, parent_branch: Optional[str] = None) -> bool:
        """Initialize a new branch with optional parent context"""
        try:
            if parent_branch:
                parent_info = self.get_branch_info(parent_branch)
                if parent_info:
                    # Copy parent's backup as starting point
                    parent_backup = Path(parent_info['backupFile'])
                    if parent_backup.exists():
                        child_backup = self.get_branch_backup_file(branch)
                        shutil.copy2(parent_backup, child_backup)

                        # Update metadata
                        metadata = self.load_metadata()
                        metadata['branches'][branch] = {
                            'parentBranch': parent_branch,
                            'backupFile': str(child_backup),
                            'messageCount': parent_info['messageCount'],
                            'created': datetime.now().isoformat(),
                            'inheritedFrom': parent_branch
                        }
                        self.save_metadata(metadata)

                        print(f"✓ Initialized branch '{branch}' with context from '{parent_branch}'")
                        return True

            # No parent or parent not found - create empty
            metadata = self.load_metadata()
            metadata['branches'][branch] = {
                'parentBranch': parent_branch,
                'backupFile': str(self.get_branch_backup_file(branch)),
                'messageCount': 0,
                'created': datetime.now().isoformat()
            }
            self.save_metadata(metadata)

            print(f"✓ Initialized branch '{branch}' with fresh session")
            return True

        except Exception as e:
            print(f"Error initializing branch: {e}")
            return False

    def save_stash_context(self, stash_name: Optional[str] = None) -> bool:
        """Save chat context when creating a stash"""
        try:
            branch = self.get_current_branch()
            session_id = self.get_current_session_id()

            if not session_id:
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                return False

            # Create stash reference
            stash_ref = stash_name or f"stash-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            stash_file = self.sync_dir / 'stashes' / f"{branch}-{stash_ref}.jsonl"
            stash_file.parent.mkdir(exist_ok=True)

            # Backup current session
            shutil.copy2(session_file, stash_file)

            # Count messages
            with open(stash_file, 'r') as f:
                message_count = sum(1 for line in f if line.strip())

            # Update metadata
            metadata = self.load_metadata()
            if 'stashes' not in metadata:
                metadata['stashes'] = {}

            metadata['stashes'][stash_ref] = {
                'branch': branch,
                'backupFile': str(stash_file),
                'messageCount': message_count,
                'created': datetime.now().isoformat(),
                'sessionId': session_id
            }
            self.save_metadata(metadata)

            print(f"✓ Saved chat context for stash: {stash_ref}")
            return True

        except Exception as e:
            print(f"Error saving stash context: {e}")
            return False

    def restore_stash_context(self, stash_ref: Optional[str] = None) -> bool:
        """Restore chat context when popping/applying a stash"""
        try:
            metadata = self.load_metadata()
            stashes = metadata.get('stashes', {})

            if not stashes:
                return False

            # If no stash specified, use most recent
            if not stash_ref:
                sorted_stashes = sorted(stashes.items(),
                                      key=lambda x: x[1].get('created', ''),
                                      reverse=True)
                if not sorted_stashes:
                    return False
                stash_ref, stash_info = sorted_stashes[0]
            else:
                stash_info = stashes.get(stash_ref)
                if not stash_info:
                    print(f"Stash not found: {stash_ref}")
                    return False

            # Get current session
            session_id = self.get_current_session_id()
            if not session_id:
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                return False

            # Restore from stash backup
            stash_file = Path(stash_info['backupFile'])
            if stash_file.exists():
                shutil.copy2(stash_file, session_file)
                print(f"✓ Restored chat context from stash: {stash_ref}")
                print(f"   Messages: {stash_info.get('messageCount', 0)}")
                return True
            else:
                print(f"Stash backup not found: {stash_file}")
                return False

        except Exception as e:
            print(f"Error restoring stash context: {e}")
            return False

    def list_stashes(self) -> Dict[str, Dict]:
        """List all saved stash contexts"""
        metadata = self.load_metadata()
        return metadata.get('stashes', {})

    def save_pre_rebase_backup(self, branch: str, base_commit: str) -> bool:
        """Save backup before rebase operation

        Args:
            branch: Current branch name
            base_commit: Base commit SHA for rebase

        Returns:
            True if successful, False otherwise
        """
        try:
            session_id = self.get_current_session_id()
            if not session_id:
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                return False

            # Get current commit SHA
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            current_sha = result.stdout.strip()[:7]

            # Create backup filename
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_filename = f"{branch}_{current_sha}_before_rebase_onto_{base_commit[:7]}_{timestamp}.jsonl"
            backup_dir = self.sync_dir / 'rebase-backups'
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / backup_filename

            # Copy current session
            shutil.copy2(session_file, backup_file)

            # Count messages
            with open(backup_file, 'r') as f:
                message_count = sum(1 for line in f if line.strip())

            # Update metadata
            metadata = self.load_metadata()
            if 'rebaseBackups' not in metadata:
                metadata['rebaseBackups'] = []

            metadata['rebaseBackups'].append({
                'branch': branch,
                'originalSHA': current_sha,
                'baseCommit': base_commit[:7],
                'backupFile': str(backup_file),
                'timestamp': datetime.now().isoformat(),
                'messageCount': message_count
            })
            self.save_metadata(metadata)

            print(f"✓ Saved pre-rebase backup: {message_count} messages")
            return True

        except Exception as e:
            print(f"Error saving pre-rebase backup: {e}")
            return False

    def handle_rebase_complete(self, commit_mappings: str) -> bool:
        """Handle post-rebase cleanup and marker

        Args:
            commit_mappings: Commit mapping from stdin (old_sha new_sha per line)

        Returns:
            True if successful, False otherwise
        """
        try:
            branch = self.get_current_branch()
            session_id = self.get_current_session_id()

            if not session_id:
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                return False

            # Parse commit mappings
            mappings = []
            for line in commit_mappings.strip().split('\n'):
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        mappings.append({
                            'old': parts[0][:7],
                            'new': parts[1][:7]
                        })

            # Add rebase marker to session
            rebase_marker = {
                'role': 'system',
                'content': f'[Rebase completed on {branch}]',
                'timestamp': datetime.now().isoformat(),
                'rebase': {
                    'branch': branch,
                    'commitMappings': mappings,
                    'timestamp': datetime.now().isoformat()
                }
            }

            # Append marker to session file
            with open(session_file, 'a') as f:
                f.write(json.dumps(rebase_marker) + '\n')

            # Update metadata
            metadata = self.load_metadata()
            if branch in metadata.get('branches', {}):
                metadata['branches'][branch]['lastRebase'] = datetime.now().isoformat()
                self.save_metadata(metadata)

            return True

        except Exception as e:
            print(f"Error handling rebase completion: {e}")
            return False

    def archive_branch_session(self, branch: str) -> bool:
        """Archive a branch session to archived-sessions directory

        Args:
            branch: Branch name to archive

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get session path (handles both compressed and uncompressed)
            session_path = self.storage.get_session_path(branch)

            if not session_path:
                print(f"Session not found for branch: {branch}")
                return False

            # Create archive filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            archive_filename = f"{branch}_{timestamp}{session_path.suffix}"
            archive_dir = self.sync_dir / 'archived-sessions'
            archive_dir.mkdir(exist_ok=True)
            archive_file = archive_dir / archive_filename

            # Move session to archive
            shutil.move(str(session_path), str(archive_file))

            # Update metadata
            metadata = self.load_metadata()

            # Remove from active branches
            branch_info = metadata.get('branches', {}).pop(branch, None)

            # Add to archived branches
            if 'archivedBranches' not in metadata:
                metadata['archivedBranches'] = {}

            metadata['archivedBranches'][branch] = {
                'archivedDate': datetime.now().isoformat(),
                'archiveFile': str(archive_file),
                'originalInfo': branch_info
            }

            self.save_metadata(metadata)

            print(f"✓ Archived session for branch: {branch}")
            return True

        except Exception as e:
            print(f"Error archiving branch session: {e}")
            return False

    def get_orphaned_branches(self) -> List[str]:
        """Find branches in metadata that don't exist in Git

        Returns:
            List of orphaned branch names
        """
        try:
            # Get all branches from Git
            result = subprocess.run(
                ['git', 'branch', '--format=%(refname:short)'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            git_branches = set(result.stdout.strip().split('\n'))

            # Get all branches from metadata
            metadata = self.load_metadata()
            metadata_branches = set(metadata.get('branches', {}).keys())

            # Find orphaned branches
            orphaned = metadata_branches - git_branches

            return list(orphaned)

        except Exception as e:
            print(f"Error finding orphaned branches: {e}")
            return []

    def prune_old_branches(self, days: int = 30, dry_run: bool = False) -> Dict:
        """Remove archived branches older than specified days

        Args:
            days: Maximum age in days
            dry_run: If True, only show what would be deleted

        Returns:
            Dictionary with pruning results
        """
        try:
            results = {
                'deleted': [],
                'would_delete': [],
                'errors': [],
                'space_freed': 0
            }

            metadata = self.load_metadata()
            archived_branches = metadata.get('archivedBranches', {})

            if not archived_branches:
                print("No archived branches found")
                return results

            cutoff_date = datetime.now() - timedelta(days=days)

            for branch, info in list(archived_branches.items()):
                archive_date = datetime.fromisoformat(info['archivedDate'])

                if archive_date < cutoff_date:
                    archive_file = Path(info['archiveFile'])
                    age_days = (datetime.now() - archive_date).days

                    if dry_run:
                        size = archive_file.stat().st_size if archive_file.exists() else 0
                        results['would_delete'].append({
                            'branch': branch,
                            'age_days': age_days,
                            'size_bytes': size
                        })
                    else:
                        try:
                            size = archive_file.stat().st_size if archive_file.exists() else 0
                            if archive_file.exists():
                                archive_file.unlink()

                            # Remove from metadata
                            del archived_branches[branch]

                            results['deleted'].append(branch)
                            results['space_freed'] += size

                        except Exception as e:
                            results['errors'].append(f"Error deleting {branch}: {e}")

            # Save updated metadata if not dry run
            if not dry_run and results['deleted']:
                metadata['archivedBranches'] = archived_branches
                self.save_metadata(metadata)

            return results

        except Exception as e:
            print(f"Error pruning old branches: {e}")
            return {'deleted': [], 'would_delete': [], 'errors': [str(e)], 'space_freed': 0}

    def list_archived_branches(self) -> Dict[str, Dict]:
        """List all archived branches

        Returns:
            Dictionary of archived branch information
        """
        metadata = self.load_metadata()
        return metadata.get('archivedBranches', {})

    def save_tag_snapshot(self, tag_name: str, description: Optional[str] = None) -> bool:
        """Save a snapshot of current session at a Git tag

        Args:
            tag_name: Git tag name
            description: Optional description for the snapshot

        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify tag exists
            result = subprocess.run(
                ['git', 'rev-parse', '--verify', f'refs/tags/{tag_name}'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode != 0:
                print(f"Git tag not found: {tag_name}")
                return False

            # Get tag commit SHA
            commit_sha = result.stdout.strip()[:7]

            # Get current branch
            branch = self.get_current_branch()

            # Get current session
            session_id = self.get_current_session_id()
            if not session_id:
                print("No active session found")
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                print("Session file not found")
                return False

            # Create safe filename from tag name
            safe_tag_name = tag_name.replace('/', '-').replace(' ', '_')
            tag_file = self.sync_dir / 'tags' / f'{safe_tag_name}.jsonl'
            tag_file.parent.mkdir(exist_ok=True)

            # Copy session to tag snapshot
            shutil.copy2(session_file, tag_file)

            # Count messages
            message_count = self.storage.count_messages(safe_tag_name.replace('.jsonl', ''))

            # Update metadata
            metadata = self.load_metadata()
            if 'tags' not in metadata:
                metadata['tags'] = {}

            metadata['tags'][tag_name] = {
                'branch': branch,
                'commitSHA': commit_sha,
                'tagFile': str(tag_file),
                'messageCount': message_count,
                'created': datetime.now().isoformat(),
                'description': description
            }
            self.save_metadata(metadata)

            print(f"✓ Saved tag snapshot: {tag_name} ({message_count} messages)")
            if description:
                print(f"  Description: {description}")

            return True

        except Exception as e:
            print(f"Error saving tag snapshot: {e}")
            return False

    def restore_tag_snapshot(self, tag_name: str) -> bool:
        """Restore session from a tag snapshot

        Args:
            tag_name: Tag name to restore from

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = self.load_metadata()
            tags = metadata.get('tags', {})

            if tag_name not in tags:
                print(f"Tag snapshot not found: {tag_name}")
                return False

            tag_info = tags[tag_name]
            tag_file = Path(tag_info['tagFile'])

            if not tag_file.exists():
                print(f"Tag snapshot file not found: {tag_file}")
                return False

            # Get current session
            session_id = self.get_current_session_id()
            if not session_id:
                print("No active session found")
                return False

            session_file = self.get_session_file(session_id)
            if not session_file:
                print("Could not find current session file")
                return False

            # Restore from tag snapshot
            shutil.copy2(tag_file, session_file)

            message_count = tag_info['messageCount']
            print(f"✓ Restored {message_count} messages from tag: {tag_name}")

            return True

        except Exception as e:
            print(f"Error restoring tag snapshot: {e}")
            return False

    def list_tag_snapshots(self) -> Dict[str, Dict]:
        """List all tag snapshots

        Returns:
            Dictionary of tag snapshot information
        """
        metadata = self.load_metadata()
        return metadata.get('tags', {})

    def delete_tag_snapshot(self, tag_name: str) -> bool:
        """Delete a tag snapshot

        Args:
            tag_name: Tag name to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            metadata = self.load_metadata()
            tags = metadata.get('tags', {})

            if tag_name not in tags:
                print(f"Tag snapshot not found: {tag_name}")
                return False

            tag_info = tags[tag_name]
            tag_file = Path(tag_info['tagFile'])

            # Delete file if it exists
            if tag_file.exists():
                tag_file.unlink()

            # Remove from metadata
            del tags[tag_name]
            self.save_metadata(metadata)

            print(f"✓ Deleted tag snapshot: {tag_name}")
            return True

        except Exception as e:
            print(f"Error deleting tag snapshot: {e}")
            return False
