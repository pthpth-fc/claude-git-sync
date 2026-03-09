#!/usr/bin/env python3
"""
Branch Context Loader for Claude Code Hooks
Saves the outgoing branch's chat and loads the incoming branch's
chat history as additionalContext JSON for Claude Code to consume.
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from claude_session_manager import ClaudeSessionManager


def extract_chat_summary(session_file: Path, max_messages: int = 50) -> str:
    """Extract a readable summary from a branch's saved session file.

    Reads the JSONL session backup and formats recent messages
    into a context string that Claude can understand.

    Args:
        session_file: Path to the .jsonl or .jsonl.gz session file
        max_messages: Maximum number of recent messages to include

    Returns:
        Formatted string of the conversation history
    """
    if not session_file.exists():
        return ""

    messages = []

    try:
        # Handle both plain and gzip files
        if str(session_file).endswith('.gz'):
            import gzip
            opener = gzip.open
        else:
            opener = open

        with opener(session_file, 'rt') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')

                    # Handle content that's a list (tool use messages)
                    if isinstance(content, list):
                        text_parts = []
                        for part in content:
                            if isinstance(part, dict) and part.get('type') == 'text':
                                text_parts.append(part.get('text', ''))
                        content = '\n'.join(text_parts)

                    if content and role in ('human', 'assistant', 'user'):
                        messages.append({
                            'role': role,
                            'content': content[:500]  # Truncate long messages
                        })
                except (json.JSONDecodeError, KeyError):
                    continue

    except Exception:
        return ""

    if not messages:
        return ""

    # Take the most recent messages
    recent = messages[-max_messages:]

    # Format into readable context
    lines = []
    for msg in recent:
        role_label = "User" if msg['role'] in ('human', 'user') else "Assistant"
        content_preview = msg['content'].replace('\n', '\n  ')
        lines.append(f"[{role_label}]: {content_preview}")

    return '\n\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Load branch chat context')
    parser.add_argument('--repo-root', required=True, help='Git repository root')
    parser.add_argument('--previous-branch', required=True, help='Branch we switched from')
    parser.add_argument('--current-branch', required=True, help='Branch we switched to')
    parser.add_argument('--max-messages', type=int, default=50,
                        help='Max messages to include in context')
    args = parser.parse_args()

    try:
        # Suppress stdout from manager methods so only our JSON goes to stdout
        import io
        import contextlib

        manager = ClaudeSessionManager(args.repo_root)

        # Step 1: Save the outgoing branch's current session
        with contextlib.redirect_stdout(io.StringIO()):
            manager.backup_current_session(args.previous_branch)

        # Step 2: Load the incoming branch's saved chat history
        backup_file = manager.get_branch_backup_file(args.current_branch)

        # Also check for compressed version
        if not backup_file.exists():
            gz_file = backup_file.with_suffix('.jsonl.gz')
            if gz_file.exists():
                backup_file = gz_file

        context_parts = []
        context_parts.append(
            f"[Branch Switch] You switched from '{args.previous_branch}' "
            f"to '{args.current_branch}'."
        )

        if backup_file.exists():
            chat_history = extract_chat_summary(backup_file, args.max_messages)
            if chat_history:
                context_parts.append(
                    f"Here is your previous conversation history on "
                    f"branch '{args.current_branch}':"
                )
                context_parts.append(chat_history)
                context_parts.append(
                    "--- End of previous conversation on "
                    f"'{args.current_branch}' ---"
                )
            else:
                context_parts.append(
                    f"No previous conversation found for branch "
                    f"'{args.current_branch}'. Starting fresh."
                )
        else:
            # Check if this branch has a parent we can inherit from
            metadata = manager.load_metadata()
            parent_branches = metadata.get('branches', {})

            context_parts.append(
                f"No previous conversation found for branch "
                f"'{args.current_branch}'. Starting fresh."
            )

            if parent_branches:
                available = ', '.join(parent_branches.keys())
                context_parts.append(
                    f"Branches with saved context: {available}"
                )

        # Step 3: Update metadata to reflect branch switch
        metadata = manager.load_metadata()
        metadata['currentBranch'] = args.current_branch
        manager.save_metadata(metadata)

        # Output JSON for Claude Code's additionalContext
        output = {
            "additionalContext": '\n\n'.join(context_parts)
        }
        print(json.dumps(output))

    except Exception as e:
        # On error, still output valid JSON with a notice
        output = {
            "additionalContext": (
                f"[Branch Switch] Switched to '{args.current_branch}'. "
                f"(Context load failed: {e})"
            )
        }
        print(json.dumps(output))


if __name__ == '__main__':
    main()
