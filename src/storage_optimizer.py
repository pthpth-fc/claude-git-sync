#!/usr/bin/env python3
"""
Storage Optimizer for Claude Git Sync
Handles compression, deduplication, and search indexing
"""

import gzip
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class StorageOptimizer:
    """Compression, deduplication, and search indexing"""

    def __init__(self, sync_dir: Path, config):
        """Initialize storage optimizer

        Args:
            sync_dir: Path to .claude-git-sync directory
            config: ConfigManager instance
        """
        self.sync_dir = sync_dir
        self.sessions_dir = sync_dir / 'sessions'
        self.config = config

    def compress_session(self, branch: str) -> bool:
        """Compress a session file to .jsonl.gz format

        Args:
            branch: Branch name

        Returns:
            True if successful, False otherwise
        """
        session_file = self.sessions_dir / f"{branch}.jsonl"

        if not session_file.exists():
            print(f"Session file not found: {branch}.jsonl")
            return False

        # Check if already compressed
        if (self.sessions_dir / f"{branch}.jsonl.gz").exists():
            print(f"Session already compressed: {branch}")
            return True

        try:
            # Read uncompressed file
            with open(session_file, 'rb') as f_in:
                # Write compressed file
                with gzip.open(f"{session_file}.gz", 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove uncompressed file
            session_file.unlink()

            print(f"✓ Compressed: {branch}.jsonl → {branch}.jsonl.gz")
            return True

        except Exception as e:
            print(f"Error compressing session {branch}: {e}")
            return False

    def decompress_session(self, branch: str) -> Optional[Path]:
        """Decompress a session file (transparent operation)

        Args:
            branch: Branch name

        Returns:
            Path to uncompressed file or None if failed
        """
        compressed_file = self.sessions_dir / f"{branch}.jsonl.gz"

        if not compressed_file.exists():
            # Not compressed, return uncompressed path if it exists
            uncompressed_file = self.sessions_dir / f"{branch}.jsonl"
            return uncompressed_file if uncompressed_file.exists() else None

        try:
            uncompressed_file = self.sessions_dir / f"{branch}.jsonl"

            # Read compressed file
            with gzip.open(compressed_file, 'rb') as f_in:
                # Write uncompressed file
                with open(uncompressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Remove compressed file
            compressed_file.unlink()

            return uncompressed_file

        except Exception as e:
            print(f"Error decompressing session {branch}: {e}")
            return None

    def get_session_path(self, branch: str) -> Optional[Path]:
        """Get the path to a session file (handles both compressed and uncompressed)

        Args:
            branch: Branch name

        Returns:
            Path to session file or None if not found
        """
        # Check for uncompressed file first
        uncompressed = self.sessions_dir / f"{branch}.jsonl"
        if uncompressed.exists():
            return uncompressed

        # Check for compressed file
        compressed = self.sessions_dir / f"{branch}.jsonl.gz"
        if compressed.exists():
            return compressed

        return None

    def read_session(self, branch: str, compressed_ok: bool = True):
        """Read a session file (handles both compressed and uncompressed)

        Args:
            branch: Branch name
            compressed_ok: If True, can read compressed files directly

        Yields:
            Parsed JSON objects from session file
        """
        session_path = self.get_session_path(branch)

        if not session_path:
            return

        try:
            if session_path.suffix == '.gz':
                # Compressed file
                with gzip.open(session_path, 'rt', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            yield json.loads(line)
            else:
                # Uncompressed file
                with open(session_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            yield json.loads(line)

        except Exception as e:
            print(f"Error reading session {branch}: {e}")

    def count_messages(self, branch: str) -> int:
        """Count messages in a session file

        Args:
            branch: Branch name

        Returns:
            Number of messages
        """
        count = 0
        for _ in self.read_session(branch):
            count += 1
        return count

    def get_file_age_days(self, file_path: Path) -> int:
        """Get age of file in days

        Args:
            file_path: Path to file

        Returns:
            Age in days
        """
        if not file_path.exists():
            return 0

        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        age = datetime.now() - modified_time
        return age.days

    def find_compressible_sessions(self) -> List[Dict[str, any]]:
        """Find sessions that should be compressed

        Returns:
            List of dictionaries with session info
        """
        compressible = []
        threshold = self.config.get('compression.threshold', 1000)

        # Find all uncompressed session files
        for session_file in self.sessions_dir.glob('*.jsonl'):
            branch = session_file.stem

            # Count messages
            message_count = self.count_messages(branch)

            # Get file age
            age_days = self.get_file_age_days(session_file)

            # Determine if compressible
            should_compress = False
            reason = ""

            if message_count >= threshold:
                should_compress = True
                reason = f"exceeds threshold ({message_count} >= {threshold} messages)"
            elif age_days >= 90:
                should_compress = True
                reason = f"old session ({age_days} days)"

            if should_compress:
                compressible.append({
                    'branch': branch,
                    'messages': message_count,
                    'age_days': age_days,
                    'size_bytes': session_file.stat().st_size,
                    'reason': reason
                })

        return compressible

    def get_storage_stats(self) -> Dict[str, any]:
        """Get storage statistics

        Returns:
            Dictionary with storage stats
        """
        stats = {
            'total_sessions': 0,
            'compressed_sessions': 0,
            'uncompressed_sessions': 0,
            'total_messages': 0,
            'total_size_bytes': 0,
            'compressed_size_bytes': 0,
            'uncompressed_size_bytes': 0,
            'sessions': []
        }

        # Scan all session files
        for session_file in self.sessions_dir.glob('*.jsonl*'):
            if session_file.name.endswith('.jsonl.gz'):
                branch = session_file.name[:-9]  # Remove .jsonl.gz
                is_compressed = True
            elif session_file.name.endswith('.jsonl'):
                branch = session_file.name[:-6]  # Remove .jsonl
                is_compressed = False
            else:
                continue

            # Skip if we already processed this branch (compressed version)
            if any(s['branch'] == branch for s in stats['sessions']):
                continue

            message_count = self.count_messages(branch)
            size_bytes = session_file.stat().st_size
            age_days = self.get_file_age_days(session_file)

            stats['total_sessions'] += 1
            stats['total_messages'] += message_count
            stats['total_size_bytes'] += size_bytes

            if is_compressed:
                stats['compressed_sessions'] += 1
                stats['compressed_size_bytes'] += size_bytes
            else:
                stats['uncompressed_sessions'] += 1
                stats['uncompressed_size_bytes'] += size_bytes

            stats['sessions'].append({
                'branch': branch,
                'messages': message_count,
                'size_bytes': size_bytes,
                'age_days': age_days,
                'compressed': is_compressed
            })

        return stats

    def vacuum(self) -> Dict[str, any]:
        """Perform full optimization

        Returns:
            Dictionary with optimization results
        """
        print("\n🔧 Starting storage optimization...")
        print("=" * 50)

        results = {
            'compressed_count': 0,
            'space_saved': 0,
            'errors': []
        }

        # Find compressible sessions
        compressible = self.find_compressible_sessions()

        if not compressible:
            print("✓ No sessions need compression")
        else:
            print(f"\nFound {len(compressible)} session(s) to compress:")
            for session in compressible:
                print(f"  - {session['branch']}: {session['reason']}")

            # Compress each session
            print("\nCompressing...")
            for session in compressible:
                size_before = session['size_bytes']
                if self.compress_session(session['branch']):
                    # Get compressed size
                    compressed_path = self.sessions_dir / f"{session['branch']}.jsonl.gz"
                    if compressed_path.exists():
                        size_after = compressed_path.stat().st_size
                        saved = size_before - size_after
                        results['compressed_count'] += 1
                        results['space_saved'] += saved
                        print(f"  Saved {self._format_bytes(saved)} ({self._format_percent(saved, size_before)})")
                else:
                    results['errors'].append(f"Failed to compress {session['branch']}")

        # Show final stats
        print("\n" + "=" * 50)
        print("Optimization Complete!")
        print(f"  Compressed: {results['compressed_count']} session(s)")
        print(f"  Space saved: {self._format_bytes(results['space_saved'])}")

        if results['errors']:
            print(f"\nErrors:")
            for error in results['errors']:
                print(f"  - {error}")

        return results

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes as human-readable string

        Args:
            bytes_count: Number of bytes

        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"

    def _format_percent(self, part: int, total: int) -> str:
        """Format percentage

        Args:
            part: Part value
            total: Total value

        Returns:
            Formatted percentage string
        """
        if total == 0:
            return "0%"
        percent = (part / total) * 100
        return f"{percent:.1f}%"

    def build_search_index(self) -> bool:
        """Build search index for fast lookups

        Returns:
            True if successful
        """
        try:
            print("\n🔍 Building search index...")

            index = {
                'files': {},       # file_path: [(branch, msg_id)]
                'keywords': {},    # keyword: [(branch, msg_id)]
                'branches': {},    # branch: {msg_count, files[]}
                'built': datetime.now().isoformat()
            }

            # Get all branches from metadata
            import json
            metadata_file = self.sync_dir / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                branches = list(metadata.get('branches', {}).keys())
            else:
                branches = []

            total_messages = 0

            for branch in branches:
                files_mentioned = set()
                msg_count = 0

                for i, msg in enumerate(self.read_session(branch)):
                    msg_count += 1
                    total_messages += 1
                    content = msg.get('content', '')

                    # Index file mentions
                    # Look for common file patterns
                    import re
                    file_patterns = [
                        r'[\w/-]+\.\w+',  # filename.ext
                        r'[\w/-]+/[\w/-]+',  # path/to/file
                    ]

                    for pattern in file_patterns:
                        matches = re.findall(pattern, content)
                        for match in matches:
                            if '.' in match or '/' in match:  # Likely a file
                                files_mentioned.add(match)

                                if match not in index['files']:
                                    index['files'][match] = []
                                index['files'][match].append((branch, i))

                    # Index keywords (common technical terms)
                    # Extract words that might be search terms
                    words = re.findall(r'\b\w{4,}\b', content.lower())
                    for word in set(words):  # Unique words only
                        # Skip common words
                        if word in ['this', 'that', 'with', 'from', 'have', 'will',
                                   'what', 'when', 'where', 'which', 'your', 'their']:
                            continue

                        if word not in index['keywords']:
                            index['keywords'][word] = []

                        # Limit to first 100 occurrences per keyword
                        if len(index['keywords'][word]) < 100:
                            index['keywords'][word].append((branch, i))

                # Store branch info
                index['branches'][branch] = {
                    'msg_count': msg_count,
                    'files': list(files_mentioned)
                }

            # Save index
            index_file = self.sync_dir / '.search-index.json'
            with open(index_file, 'w') as f:
                json.dump(index, f, indent=2)

            print(f"✓ Search index built:")
            print(f"  Indexed {total_messages} messages across {len(branches)} branches")
            print(f"  Found {len(index['files'])} unique file references")
            print(f"  Indexed {len(index['keywords'])} keywords")

            return True

        except Exception as e:
            print(f"Error building search index: {e}")
            return False

    def deduplicate_child_sessions(self) -> Dict:
        """Remove inherited messages from child branches

        This creates delta files that only store new messages,
        reducing storage for branches with shared history.

        Returns:
            Dictionary with deduplication results
        """
        try:
            print("\n🔗 Deduplicating child branch sessions...")

            results = {
                'deduplicated': 0,
                'space_saved': 0,
                'errors': []
            }

            # Get metadata to find parent-child relationships
            import json
            metadata_file = self.sync_dir / 'metadata.json'
            if not metadata_file.exists():
                print("No metadata found")
                return results

            with open(metadata_file, 'r') as f:
                metadata = json.load(f)

            branches = metadata.get('branches', {})

            # Find branches with parents
            for branch, info in branches.items():
                parent = info.get('parentBranch')
                if not parent or parent not in branches:
                    continue

                # Check if already deduplicated
                if info.get('deduplicated'):
                    continue

                # Load parent messages
                parent_messages = list(self.read_session(parent))
                parent_contents = [msg.get('content', '') for msg in parent_messages]

                # Load child messages
                child_messages = list(self.read_session(branch))

                # Find unique messages in child
                unique_messages = []
                for msg in child_messages:
                    if msg.get('content', '') not in parent_contents:
                        unique_messages.append(msg)

                # Calculate space savings
                original_size = self.get_session_path(branch)
                if original_size:
                    original_size = original_size.stat().st_size

                # Only deduplicate if there's significant overlap
                overlap_ratio = 1 - (len(unique_messages) / len(child_messages)) if child_messages else 0

                if overlap_ratio < 0.3:  # Less than 30% overlap, not worth it
                    continue

                # Create delta file
                delta_file = self.sessions_dir / f"{branch}.delta.jsonl"

                with open(delta_file, 'w') as f:
                    for msg in unique_messages:
                        f.write(json.dumps(msg) + '\n')

                # Remove original file
                original_file = self.get_session_path(branch)
                if original_file and original_file.exists():
                    new_size = delta_file.stat().st_size
                    space_saved = original_size - new_size

                    original_file.unlink()

                    # Update metadata
                    branches[branch]['deduplicated'] = True
                    branches[branch]['deltaFile'] = str(delta_file)
                    branches[branch]['uniqueMessages'] = len(unique_messages)

                    results['deduplicated'] += 1
                    results['space_saved'] += space_saved

                    print(f"  ✓ {branch}: {len(child_messages)} → {len(unique_messages)} messages "
                          f"(saved {self._format_bytes(space_saved)})")

            # Save updated metadata
            if results['deduplicated'] > 0:
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)

            if results['deduplicated'] == 0:
                print("  No branches to deduplicate")
            else:
                print(f"\n✓ Deduplicated {results['deduplicated']} branch(es)")
                print(f"  Space saved: {self._format_bytes(results['space_saved'])}")

            return results

        except Exception as e:
            print(f"Error deduplicating sessions: {e}")
            return {'deduplicated': 0, 'space_saved': 0, 'errors': [str(e)]}

    def vacuum_complete(self) -> Dict:
        """Perform comprehensive optimization

        Runs all optimization operations:
        1. Compress old/large sessions
        2. Deduplicate child branches
        3. Build search index
        4. Clean temp files

        Returns:
            Dictionary with optimization results
        """
        print("\n🔧 Starting comprehensive optimization...")
        print("=" * 60)

        all_results = {
            'compression': {},
            'deduplication': {},
            'indexing': False,
            'cleanup': 0
        }

        # 1. Compress sessions
        print("\n[1/4] Compressing sessions...")
        all_results['compression'] = self.vacuum()

        # 2. Deduplicate child branches
        print("\n[2/4] Deduplicating child branches...")
        all_results['deduplication'] = self.deduplicate_child_sessions()

        # 3. Build search index
        print("\n[3/4] Building search index...")
        all_results['indexing'] = self.build_search_index()

        # 4. Clean temp files
        print("\n[4/4] Cleaning temporary files...")
        temp_files = list(self.sync_dir.glob('*.tmp'))
        temp_files.extend(list(self.sync_dir.glob('**/*.tmp')))

        for temp_file in temp_files:
            try:
                temp_file.unlink()
                all_results['cleanup'] += 1
            except:
                pass

        if all_results['cleanup'] > 0:
            print(f"  ✓ Cleaned {all_results['cleanup']} temporary file(s)")
        else:
            print("  No temporary files to clean")

        # Final summary
        print("\n" + "=" * 60)
        print("🎉 Optimization Complete!")

        total_saved = (all_results['compression'].get('space_saved', 0) +
                      all_results['deduplication'].get('space_saved', 0))

        if total_saved > 0:
            print(f"Total space saved: {self._format_bytes(total_saved)}")

        print("=" * 60)

        return all_results
