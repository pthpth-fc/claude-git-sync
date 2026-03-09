#!/usr/bin/env python3
"""
History Viewer for Claude Git Sync
Timeline viewing, searching, diffing, and statistics
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Iterator, Tuple
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Search result with context"""
    branch: str
    message_index: int
    role: str
    content: str
    timestamp: Optional[str]
    match_line: int
    context_before: List[str]
    context_after: List[str]


@dataclass
class DiffResult:
    """Branch comparison result"""
    branch1: str
    branch2: str
    messages1: int
    messages2: int
    common_count: int
    unique1: List[Dict]
    unique2: List[Dict]


@dataclass
class Stats:
    """Session statistics"""
    total_messages: int
    by_role: Dict[str, int]
    first_message_date: Optional[str]
    last_message_date: Optional[str]
    total_branches: int
    storage_bytes: int


class HistoryViewer:
    """Timeline viewing, searching, diffing, statistics"""

    def __init__(self, manager, storage):
        """Initialize history viewer

        Args:
            manager: ClaudeSessionManager instance
            storage: StorageOptimizer instance
        """
        self.manager = manager
        self.storage = storage
        self.sync_dir = manager.sync_dir

    def show_timeline(self,
                     branch: str,
                     limit: int = 20,
                     offset: int = 0,
                     role_filter: Optional[str] = None,
                     date_from: Optional[str] = None,
                     date_to: Optional[str] = None,
                     output_format: str = 'timeline') -> bool:
        """Show timeline of messages

        Args:
            branch: Branch name
            limit: Number of messages to show
            offset: Number of messages to skip
            role_filter: Filter by role ('user', 'assistant', 'system')
            date_from: Filter messages from this date (ISO format)
            date_to: Filter messages to this date (ISO format)
            output_format: 'timeline', 'table', or 'json'

        Returns:
            True if successful
        """
        try:
            messages = list(self._read_messages_with_filters(
                branch, role_filter, date_from, date_to, offset, limit
            ))

            if not messages:
                print(f"No messages found for branch: {branch}")
                return False

            if output_format == 'json':
                print(json.dumps(messages, indent=2))
            elif output_format == 'table':
                self._print_table(messages)
            else:
                self._print_timeline(messages, branch)

            return True

        except Exception as e:
            print(f"Error showing timeline: {e}")
            return False

    def _read_messages_with_filters(self,
                                    branch: str,
                                    role_filter: Optional[str],
                                    date_from: Optional[str],
                                    date_to: Optional[str],
                                    offset: int,
                                    limit: int) -> Iterator[Dict]:
        """Read messages with filters applied

        Args:
            branch: Branch name
            role_filter: Filter by role
            date_from: Filter from date
            date_to: Filter to date
            offset: Skip messages
            limit: Max messages

        Yields:
            Filtered messages
        """
        count = 0
        skipped = 0

        for msg in self.storage.read_session(branch):
            # Apply role filter
            if role_filter and msg.get('role') != role_filter:
                continue

            # Apply date filters
            if date_from or date_to:
                msg_date = msg.get('timestamp')
                if msg_date:
                    if date_from and msg_date < date_from:
                        continue
                    if date_to and msg_date > date_to:
                        continue

            # Apply offset
            if skipped < offset:
                skipped += 1
                continue

            # Apply limit
            if count >= limit:
                break

            yield msg
            count += 1

    def _print_timeline(self, messages: List[Dict], branch: str):
        """Print timeline format

        Args:
            messages: List of messages
            branch: Branch name
        """
        max_preview_length = self.manager.config.get('history.maxPreviewLength', 100)
        show_timestamps = self.manager.config.get('history.showTimestamps', True)

        print(f"\n📜 Chat History: {branch}")
        print("=" * 70)

        for i, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            # Choose emoji based on role
            emoji = {
                'user': '👤',
                'assistant': '🤖',
                'system': '⚙️'
            }.get(role, '❓')

            # Format timestamp
            time_str = ''
            if show_timestamps and timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    time_str = timestamp[:19] if len(timestamp) >= 19 else timestamp

            # Truncate content for preview
            preview = content[:max_preview_length]
            if len(content) > max_preview_length:
                preview += '...'

            # Replace newlines in preview
            preview = preview.replace('\n', ' ')

            # Print message line
            if time_str:
                print(f"{emoji} [{time_str}] {role.upper()}: {preview}")
            else:
                print(f"{emoji} {role.upper()}: {preview}")

        print("=" * 70)

    def _print_table(self, messages: List[Dict]):
        """Print table format

        Args:
            messages: List of messages
        """
        max_preview = 50

        print(f"\n{'ID':<5} {'Time':<20} {'Role':<10} {'Preview':<50}")
        print("-" * 90)

        for i, msg in enumerate(messages, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')

            # Format time
            time_str = ''
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    time_str = dt.strftime('%m-%d %H:%M')
                except:
                    time_str = timestamp[:14] if len(timestamp) >= 14 else timestamp

            # Truncate preview
            preview = content[:max_preview].replace('\n', ' ')
            if len(content) > max_preview:
                preview += '...'

            print(f"{i:<5} {time_str:<20} {role:<10} {preview:<50}")

    def search_messages(self,
                       pattern: str,
                       branch: Optional[str] = None,
                       use_regex: bool = False,
                       context_lines: int = 0) -> List[SearchResult]:
        """Search for messages matching pattern

        Args:
            pattern: Search pattern
            branch: Branch to search (None = all branches)
            use_regex: Use regex matching
            context_lines: Number of context lines before/after

        Returns:
            List of search results
        """
        results = []

        # Determine branches to search
        if branch:
            branches = [branch]
        else:
            # Get all branches from metadata
            metadata = self.manager.load_metadata()
            branches = list(metadata.get('branches', {}).keys())

        # Compile regex if needed
        if use_regex:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                print(f"Invalid regex pattern: {e}")
                return []
        else:
            pattern_lower = pattern.lower()

        # Search each branch
        for branch_name in branches:
            messages = list(self.storage.read_session(branch_name))

            for i, msg in enumerate(messages):
                content = msg.get('content', '')

                # Check for match
                matched = False
                match_line = 0

                if use_regex:
                    match = regex.search(content)
                    if match:
                        matched = True
                        # Find line number of match
                        match_line = content[:match.start()].count('\n')
                else:
                    if pattern_lower in content.lower():
                        matched = True
                        match_line = content.lower().find(pattern_lower)
                        match_line = content[:match_line].count('\n')

                if matched:
                    # Get context
                    context_before = []
                    context_after = []

                    if context_lines > 0:
                        # Get previous messages
                        for j in range(max(0, i - context_lines), i):
                            context_before.append(messages[j].get('content', ''))

                        # Get next messages
                        for j in range(i + 1, min(len(messages), i + 1 + context_lines)):
                            context_after.append(messages[j].get('content', ''))

                    results.append(SearchResult(
                        branch=branch_name,
                        message_index=i,
                        role=msg.get('role', 'unknown'),
                        content=content,
                        timestamp=msg.get('timestamp'),
                        match_line=match_line,
                        context_before=context_before,
                        context_after=context_after
                    ))

        return results

    def display_search_results(self, results: List[SearchResult], pattern: str):
        """Display search results

        Args:
            results: List of search results
            pattern: Search pattern
        """
        if not results:
            print(f"No matches found for: {pattern}")
            return

        print(f"\n🔍 Search Results for '{pattern}' ({len(results)} matches):")
        print("=" * 70)

        max_preview = self.manager.config.get('history.maxPreviewLength', 100)

        for i, result in enumerate(results, 1):
            # Format timestamp
            time_str = ''
            if result.timestamp:
                try:
                    dt = datetime.fromisoformat(result.timestamp)
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = result.timestamp[:16] if len(result.timestamp) >= 16 else result.timestamp

            print(f"\n[{i}] {result.branch} (Message #{result.message_index + 1})")
            if time_str:
                print(f"    Time: {time_str}")
            print(f"    Role: {result.role}")

            # Show content preview
            preview = result.content[:max_preview].replace('\n', ' ')
            if len(result.content) > max_preview:
                preview += '...'
            print(f"    Preview: {preview}")

            # Show context if available
            if result.context_before:
                print(f"    Context before: {len(result.context_before)} message(s)")
            if result.context_after:
                print(f"    Context after: {len(result.context_after)} message(s)")

        print("\n" + "=" * 70)

    def diff_branches(self, branch1: str, branch2: str) -> Optional[DiffResult]:
        """Compare messages between two branches

        Args:
            branch1: First branch
            branch2: Second branch

        Returns:
            DiffResult or None if error
        """
        try:
            messages1 = list(self.storage.read_session(branch1))
            messages2 = list(self.storage.read_session(branch2))

            # Find common messages (same content)
            contents1 = [msg.get('content', '') for msg in messages1]
            contents2 = [msg.get('content', '') for msg in messages2]

            common_count = len(set(contents1) & set(contents2))

            # Find unique messages
            unique1 = [msg for msg in messages1 if msg.get('content', '') not in contents2]
            unique2 = [msg for msg in messages2 if msg.get('content', '') not in contents1]

            return DiffResult(
                branch1=branch1,
                branch2=branch2,
                messages1=len(messages1),
                messages2=len(messages2),
                common_count=common_count,
                unique1=unique1,
                unique2=unique2
            )

        except Exception as e:
            print(f"Error comparing branches: {e}")
            return None

    def display_diff(self, diff: DiffResult):
        """Display branch diff

        Args:
            diff: DiffResult to display
        """
        print(f"\n🔀 Branch Comparison")
        print("=" * 70)
        print(f"Branch 1: {diff.branch1} ({diff.messages1} messages)")
        print(f"Branch 2: {diff.branch2} ({diff.messages2} messages)")
        print(f"\nCommon messages: {diff.common_count}")
        print(f"Unique to {diff.branch1}: {len(diff.unique1)}")
        print(f"Unique to {diff.branch2}: {len(diff.unique2)}")

        max_preview = 60

        if diff.unique1:
            print(f"\n📝 Unique to {diff.branch1}:")
            for i, msg in enumerate(diff.unique1[:5], 1):  # Show first 5
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:max_preview].replace('\n', ' ')
                print(f"  {i}. [{role}] {content}...")

            if len(diff.unique1) > 5:
                print(f"  ... and {len(diff.unique1) - 5} more")

        if diff.unique2:
            print(f"\n📝 Unique to {diff.branch2}:")
            for i, msg in enumerate(diff.unique2[:5], 1):  # Show first 5
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:max_preview].replace('\n', ' ')
                print(f"  {i}. [{role}] {content}...")

            if len(diff.unique2) > 5:
                print(f"  ... and {len(diff.unique2) - 5} more")

        print("\n" + "=" * 70)

    def show_statistics(self, branch: Optional[str] = None) -> Stats:
        """Calculate and show statistics

        Args:
            branch: Branch to analyze (None = all branches)

        Returns:
            Stats object
        """
        try:
            metadata = self.manager.load_metadata()

            if branch:
                branches = [branch]
            else:
                branches = list(metadata.get('branches', {}).keys())

            # Calculate stats
            total_messages = 0
            by_role = {}
            first_date = None
            last_date = None

            for branch_name in branches:
                for msg in self.storage.read_session(branch_name):
                    total_messages += 1

                    # Count by role
                    role = msg.get('role', 'unknown')
                    by_role[role] = by_role.get(role, 0) + 1

                    # Track dates
                    timestamp = msg.get('timestamp')
                    if timestamp:
                        if not first_date or timestamp < first_date:
                            first_date = timestamp
                        if not last_date or timestamp > last_date:
                            last_date = timestamp

            # Calculate storage size
            storage_stats = self.storage.get_storage_stats()

            stats = Stats(
                total_messages=total_messages,
                by_role=by_role,
                first_message_date=first_date,
                last_message_date=last_date,
                total_branches=len(branches),
                storage_bytes=storage_stats['total_size_bytes']
            )

            self.display_statistics(stats, branch)
            return stats

        except Exception as e:
            print(f"Error calculating statistics: {e}")
            return None

    def display_statistics(self, stats: Stats, branch: Optional[str] = None):
        """Display statistics

        Args:
            stats: Stats object to display
            branch: Branch name or None for all branches
        """
        scope = f"Branch: {branch}" if branch else "All Branches"

        print(f"\n📊 Statistics - {scope}")
        print("=" * 60)
        print(f"\nTotal Messages: {stats.total_messages}")

        print(f"\nMessages by Role:")
        for role, count in sorted(stats.by_role.items()):
            percentage = (count / stats.total_messages * 100) if stats.total_messages > 0 else 0
            print(f"  {role}: {count} ({percentage:.1f}%)")

        print(f"\nBranches: {stats.total_branches}")

        if stats.first_message_date:
            try:
                first = datetime.fromisoformat(stats.first_message_date)
                print(f"\nFirst Message: {first.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"\nFirst Message: {stats.first_message_date}")

        if stats.last_message_date:
            try:
                last = datetime.fromisoformat(stats.last_message_date)
                print(f"Last Message: {last.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"Last Message: {stats.last_message_date}")

        print(f"\nStorage Size: {self.storage._format_bytes(stats.storage_bytes)}")
        print("=" * 60)
