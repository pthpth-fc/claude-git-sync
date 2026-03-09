#!/usr/bin/env python3
"""
Merge Manager for Claude-Git Sync
Handles automatic merging of chat contexts when Git branches are merged
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional
import sys

sys.path.insert(0, str(Path(__file__).parent))
from claude_session_manager import ClaudeSessionManager


class MergeManager:
    def __init__(self, repo_root: Optional[str] = None):
        self.manager = ClaudeSessionManager(repo_root)

    def get_commit_sha(self, ref: str = 'HEAD') -> Optional[str]:
        """Get commit SHA for a ref"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', ref],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.manager.repo_root
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_merge_base(self, branch1: str, branch2: str) -> Optional[str]:
        """Get common ancestor of two branches"""
        try:
            result = subprocess.run(
                ['git', 'merge-base', branch1, branch2],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.manager.repo_root
            )
            return result.stdout.strip()[:8]
        except subprocess.CalledProcessError:
            return None

    def save_pre_merge_backup(self, merging_branch: str) -> bool:
        """Save chat state before merge"""
        try:
            current_branch = self.manager.get_current_branch()
            current_sha = self.get_commit_sha('HEAD')
            merging_sha = self.get_commit_sha(merging_branch)

            if not current_sha or not merging_sha:
                return False

            # Get current session
            session_id = self.manager.get_current_session_id()
            if not session_id:
                return False

            session_file = self.manager.get_session_file(session_id)
            if not session_file:
                return False

            # Create backup directory
            backup_dir = self.manager.sync_dir / 'merge-backups'
            backup_dir.mkdir(exist_ok=True)

            # Filename with commit SHAs
            backup_file = backup_dir / f"{current_branch}_{current_sha}_before_merge_{merging_branch}_{merging_sha}.jsonl"

            import shutil
            shutil.copy2(session_file, backup_file)

            # Count messages
            with open(backup_file, 'r') as f:
                message_count = sum(1 for line in f if line.strip())

            # Store in metadata
            metadata = self.manager.load_metadata()
            if 'mergeBackups' not in metadata:
                metadata['mergeBackups'] = []

            metadata['mergeBackups'].append({
                'targetBranch': current_branch,
                'targetSHA': current_sha,
                'sourceBranch': merging_branch,
                'sourceSHA': merging_sha,
                'backupFile': str(backup_file),
                'messageCount': message_count,
                'timestamp': datetime.now().isoformat()
            })
            self.manager.save_metadata(metadata)

            print(f"💾 Pre-merge backup saved")
            print(f"   Target: {current_branch} @ {current_sha} ({message_count} messages)")

            return True

        except Exception as e:
            print(f"Error saving pre-merge backup: {e}")
            return False

    def merge_chats(self, source_branch: str, strategy: str = 'append') -> bool:
        """Merge chat contexts from source branch into current"""
        try:
            current_branch = self.manager.get_current_branch()
            current_sha = self.get_commit_sha('HEAD')
            source_sha = self.get_commit_sha(source_branch)
            merge_base = self.get_merge_base(current_branch, source_branch)

            print(f"🔀 Merging chat contexts")
            print(f"   {source_branch} @ {source_sha}")
            print(f"   → {current_branch} @ {current_sha}")
            if merge_base:
                print(f"   Common ancestor: {merge_base}")

            # Get session files
            current_session_id = self.manager.get_current_session_id()
            if not current_session_id:
                print("⚠️  No active session")
                return False

            current_session_file = self.manager.get_session_file(current_session_id)
            source_backup = self.manager.get_branch_backup_file(source_branch)

            if not current_session_file:
                print("⚠️  Current session file not found")
                return False

            if not source_backup.exists():
                print(f"ℹ️  No chat history for {source_branch}, keeping current chat")
                return True

            # Read both chat histories
            with open(current_session_file, 'r') as f:
                current_lines = f.readlines()

            with open(source_backup, 'r') as f:
                source_lines = f.readlines()

            if strategy == 'append':
                # Create merge marker
                merge_marker = {
                    "type": "merge-marker",
                    "messageId": f"merge-{int(datetime.now().timestamp())}",
                    "timestamp": datetime.now().isoformat(),
                    "mergeInfo": {
                        "sourceBranch": source_branch,
                        "sourceSHA": source_sha,
                        "targetBranch": current_branch,
                        "targetSHA": current_sha,
                        "mergeBase": merge_base,
                        "strategy": "append",
                        "sourceMessages": len(source_lines),
                        "targetMessages": len(current_lines)
                    }
                }

                # Write merged content
                with open(current_session_file, 'w') as f:
                    # Current messages
                    f.writelines(current_lines)
                    # Merge marker
                    f.write(json.dumps(merge_marker) + '\n')
                    # Source messages
                    f.writelines(source_lines)

                print(f"✓ Chat contexts merged")
                print(f"   {current_branch}: {len(current_lines)} messages")
                print(f"   {source_branch}: {len(source_lines)} messages")
                print(f"   Combined: {len(current_lines) + len(source_lines)} messages")

                return True

            elif strategy == 'keep':
                # Add summary marker only
                merge_marker = {
                    "type": "merge-summary",
                    "messageId": f"merge-{int(datetime.now().timestamp())}",
                    "timestamp": datetime.now().isoformat(),
                    "mergeInfo": {
                        "sourceBranch": source_branch,
                        "sourceSHA": source_sha,
                        "targetBranch": current_branch,
                        "targetSHA": current_sha,
                        "mergeBase": merge_base,
                        "strategy": "keep",
                        "note": f"Kept {current_branch} chat, discarded {source_branch} chat"
                    }
                }

                with open(current_session_file, 'a') as f:
                    f.write(json.dumps(merge_marker) + '\n')

                print(f"✓ Kept {current_branch} chat")
                print(f"   (Discarded {source_branch} chat history)")

                return True

            else:
                print(f"Unknown strategy: {strategy}")
                return False

        except Exception as e:
            print(f"Error merging chat contexts: {e}")
            import traceback
            traceback.print_exc()
            return False

    def auto_merge(self, source_branch: str) -> bool:
        """Automatic merge handler called by post-merge hook"""
        # Save backup first
        self.save_pre_merge_backup(source_branch)

        # Default strategy: append (can be configured)
        strategy = 'append'  # Could read from config

        # Merge chats
        return self.merge_chats(source_branch, strategy)
