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


class ClaudeSessionManager:
    def __init__(self, repo_root: Optional[str] = None):
        self.repo_root = self.find_git_root() if not repo_root else repo_root
        self.claude_home = Path.home() / '.claude'
        self.sync_dir = Path(self.repo_root) / '.claude-git-sync'
        self.branch_sessions_dir = self.sync_dir / 'sessions'
        self.metadata_file = self.sync_dir / 'metadata.json'

        self.ensure_directories()

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
