#!/usr/bin/env python3
"""
Conflict Resolution Helper for Claude Git Sync
Shows relevant chat context during merge conflicts
"""

import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ConflictInfo:
    """Information about a conflicted file"""
    file_path: str
    conflict_markers: int
    ours_section: str
    theirs_section: str


@dataclass
class ChatMention:
    """Chat message mentioning a file"""
    branch: str
    message_index: int
    role: str
    content: str
    timestamp: Optional[str]
    relevance_score: float


class ConflictHelper:
    """Show relevant chat context during merge conflicts"""

    def __init__(self, manager, storage):
        """Initialize conflict helper

        Args:
            manager: ClaudeSessionManager instance
            storage: StorageOptimizer instance
        """
        self.manager = manager
        self.storage = storage
        self.repo_root = Path(manager.repo_root)

    def detect_conflicts(self) -> List[ConflictInfo]:
        """Detect current merge conflicts

        Returns:
            List of ConflictInfo objects
        """
        conflicts = []

        try:
            # Get list of conflicted files
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=U'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )

            conflicted_files = result.stdout.strip().split('\n')
            if not conflicted_files or conflicted_files == ['']:
                return []

            # Parse each conflicted file
            for file_path in conflicted_files:
                full_path = self.repo_root / file_path

                if not full_path.exists():
                    continue

                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Count conflict markers
                    marker_count = content.count('<<<<<<<')

                    # Extract OURS and THEIRS sections
                    ours_section, theirs_section = self._extract_conflict_sections(content)

                    conflicts.append(ConflictInfo(
                        file_path=file_path,
                        conflict_markers=marker_count,
                        ours_section=ours_section,
                        theirs_section=theirs_section
                    ))

                except Exception as e:
                    print(f"Warning: Could not read conflicted file {file_path}: {e}")

            return conflicts

        except subprocess.CalledProcessError:
            return []

    def _extract_conflict_sections(self, content: str) -> Tuple[str, str]:
        """Extract OURS and THEIRS sections from conflict

        Args:
            content: File content with conflict markers

        Returns:
            Tuple of (ours_section, theirs_section)
        """
        ours_parts = []
        theirs_parts = []

        # Find all conflict sections
        pattern = r'<<<<<<< .*?\n(.*?)\n=======\n(.*?)\n>>>>>>> .*?\n'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            ours_parts.append(match.group(1))
            theirs_parts.append(match.group(2))

        return '\n'.join(ours_parts), '\n'.join(theirs_parts)

    def search_chat_mentions(self, file_path: str, branch: str) -> List[ChatMention]:
        """Search chat for mentions of a file

        Args:
            file_path: File path to search for
            branch: Branch to search

        Returns:
            List of ChatMention objects
        """
        mentions = []
        file_name = Path(file_path).name
        file_stem = Path(file_path).stem

        # Search patterns
        patterns = [
            file_path,
            file_name,
            file_stem,
            file_path.replace('/', '.'),  # Module-style import
        ]

        messages = list(self.storage.read_session(branch))

        for i, msg in enumerate(messages):
            content = msg.get('content', '')
            role = msg.get('role', 'unknown')

            # Check if any pattern matches
            matched = False
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    matched = True
                    break

            if matched:
                # Calculate basic relevance score
                relevance = 0.0

                # Exact file path match
                if file_path in content:
                    relevance += 1.0

                # File name match
                if file_name in content:
                    relevance += 0.7

                # Stem match (without extension)
                if file_stem in content:
                    relevance += 0.5

                # Boost for recent messages
                recency_boost = (i / len(messages)) * 0.3
                relevance += recency_boost

                # Boost for user messages (likely requirements)
                if role == 'user':
                    relevance += 0.5

                mentions.append(ChatMention(
                    branch=branch,
                    message_index=i,
                    role=role,
                    content=content,
                    timestamp=msg.get('timestamp'),
                    relevance_score=relevance
                ))

        return mentions

    def rank_relevance(self, mentions: List[ChatMention]) -> List[ChatMention]:
        """Sort mentions by relevance score

        Args:
            mentions: List of ChatMention objects

        Returns:
            Sorted list of ChatMention objects
        """
        return sorted(mentions, key=lambda m: m.relevance_score, reverse=True)

    def display_conflict_help(self) -> bool:
        """Display conflict resolution help

        Returns:
            True if conflicts found and help displayed
        """
        print("\n🔥 Merge Conflict Helper")
        print("=" * 70)

        # Detect conflicts
        conflicts = self.detect_conflicts()

        if not conflicts:
            print("No merge conflicts detected")
            return False

        print(f"Found {len(conflicts)} conflicted file(s)\n")

        # Get current branch and merge branch
        try:
            current_branch = self.manager.get_current_branch()

            # Try to get merge head
            merge_head_file = self.repo_root / '.git' / 'MERGE_HEAD'
            merge_branch = "MERGE_BRANCH"

            if merge_head_file.exists():
                # Try to get branch name from MERGE_MSG
                merge_msg_file = self.repo_root / '.git' / 'MERGE_MSG'
                if merge_msg_file.exists():
                    with open(merge_msg_file, 'r') as f:
                        first_line = f.readline()
                        # Parse "Merge branch 'name'" message
                        match = re.search(r"Merge branch '([^']+)'", first_line)
                        if match:
                            merge_branch = match.group(1)

        except Exception as e:
            print(f"Warning: Could not determine branches: {e}")
            current_branch = "CURRENT"
            merge_branch = "MERGE"

        # Display each conflict with chat context
        for i, conflict in enumerate(conflicts, 1):
            print(f"\n[{i}] {conflict.file_path}")
            print(f"    Conflict markers: {conflict.conflict_markers}")
            print("-" * 70)

            # Search OURS branch (current)
            print(f"\n    💬 Chat context from YOUR branch ({current_branch}):")
            ours_mentions = self.search_chat_mentions(conflict.file_path, current_branch)
            ours_mentions = self.rank_relevance(ours_mentions)

            if ours_mentions:
                self._display_top_mentions(ours_mentions[:3])
            else:
                print("        No relevant chat context found")

            # Search THEIRS branch (merge)
            # Note: We may not have chat history for the merge branch
            print(f"\n    💬 Chat context from THEIR branch ({merge_branch}):")
            metadata = self.manager.load_metadata()
            if merge_branch in metadata.get('branches', {}):
                theirs_mentions = self.search_chat_mentions(conflict.file_path, merge_branch)
                theirs_mentions = self.rank_relevance(theirs_mentions)

                if theirs_mentions:
                    self._display_top_mentions(theirs_mentions[:3])
                else:
                    print("        No relevant chat context found")
            else:
                print("        (No chat history available for this branch)")

            # Show conflict preview
            print(f"\n    📄 Conflict preview:")
            if conflict.ours_section:
                preview = conflict.ours_section[:200].replace('\n', '\n        ')
                print(f"        OURS:   {preview}...")
            if conflict.theirs_section:
                preview = conflict.theirs_section[:200].replace('\n', '\n        ')
                print(f"        THEIRS: {preview}...")

            print("-" * 70)

        # Show summary and suggestions
        print(f"\n💡 Suggestions:")
        print(f"   1. Review the chat context above for each conflicted file")
        print(f"   2. Consider the original intent from the chat messages")
        print(f"   3. Resolve conflicts in your editor or IDE")
        print(f"   4. After resolving: git add <files> && git commit")
        print("\n" + "=" * 70)

        return True

    def _display_top_mentions(self, mentions: List[ChatMention], max_lines: int = 3):
        """Display top chat mentions

        Args:
            mentions: List of ChatMention objects
            max_lines: Maximum number of lines to show per mention
        """
        for mention in mentions:
            role_emoji = {
                'user': '👤',
                'assistant': '🤖',
                'system': '⚙️'
            }.get(mention.role, '❓')

            # Format timestamp
            time_str = ''
            if mention.timestamp:
                try:
                    dt = datetime.fromisoformat(mention.timestamp)
                    time_str = dt.strftime('%m-%d %H:%M')
                except (ValueError, TypeError):
                    time_str = mention.timestamp[:14] if len(mention.timestamp) >= 14 else ''

            # Show content preview
            lines = mention.content.split('\n')
            preview_lines = lines[:max_lines]
            preview = '\n        '.join(preview_lines)

            if len(lines) > max_lines:
                preview += '\n        ...'

            print(f"        {role_emoji} [{time_str}] {mention.role} (score: {mention.relevance_score:.2f}):")
            print(f"        {preview}")
            print()
