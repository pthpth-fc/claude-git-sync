#!/usr/bin/env python3
"""
Branch-Chat Manager
Handles the logic for syncing branches with chat sessions
"""

import subprocess
from datetime import datetime
from typing import Optional, List, Dict
from storage import Storage


class BranchManager:
    def __init__(self, repo_root: Optional[str] = None):
        self.storage = Storage(repo_root)

    def init_branch(self, branch: str, parent_branch: Optional[str] = None) -> str:
        """Initialize a new branch with chat session"""
        existing_chat_id = self.storage.get_chat_id_for_branch(branch)

        if existing_chat_id:
            print(f'Branch "{branch}" already has chat session: {existing_chat_id}')
            return existing_chat_id

        # Determine parent branch
        parent = parent_branch or self.storage.get_current_branch()

        # Create new chat ID
        chat_id = self.storage.generate_chat_id(branch)

        # Set up mappings
        self.storage.set_branch_mapping(branch, chat_id)

        if parent and parent != branch:
            self.storage.set_parent_branch(branch, parent)

        # Initialize chat state with inherited context
        inherited_context = self.get_inherited_context(branch)
        self.storage.save_chat_state(chat_id, {
            'branch': branch,
            'parentBranch': parent,
            'inheritedContext': inherited_context,
            'messages': [],
            'created': datetime.now().isoformat()
        })

        print(f'✓ Initialized chat session for branch "{branch}"')
        print(f'  Chat ID: {chat_id}')
        if parent and parent != branch:
            print(f'  Inherits from: {parent}')

        return chat_id

    def get_inherited_context(self, branch: str) -> List[Dict]:
        """Get inherited context from parent branches"""
        chain = self.storage.get_inheritance_chain(branch)
        contexts = []

        for ancestor in chain:
            if ancestor == branch:
                continue

            chat_id = self.storage.get_chat_id_for_branch(ancestor)
            if chat_id:
                chat_state = self.storage.load_chat_state(chat_id)
                if chat_state:
                    contexts.append({
                        'branch': ancestor,
                        'chatId': chat_id,
                        'summary': self.summarize_chat(chat_state)
                    })

        return contexts

    def summarize_chat(self, chat_state: dict) -> dict:
        """Summarize chat for inheritance"""
        return {
            'messageCount': len(chat_state.get('messages', [])),
            'lastActivity': chat_state.get('timestamp'),
            'topics': chat_state.get('topics', [])
        }

    def switch_to_branch(self, branch: str) -> Optional[dict]:
        """Switch to a branch's chat session"""
        # Check if branch exists
        if not self.storage.branch_exists(branch):
            print(f'Branch "{branch}" does not exist')
            return None

        # Get or create chat session for branch
        chat_id = self.storage.get_chat_id_for_branch(branch)

        if not chat_id:
            print(f'No chat session found for "{branch}", creating new one...')
            chat_id = self.init_branch(branch)

        chat_state = self.storage.load_chat_state(chat_id)

        print(f'\n📝 Switched to chat session for branch: {branch}')
        print(f'   Chat ID: {chat_id}')

        chain = self.storage.get_inheritance_chain(branch)
        if len(chain) > 1:
            print(f'   Inheritance: {" → ".join(chain)}')

        if chat_state and 'messages' in chat_state:
            print(f'   Messages: {len(chat_state["messages"])}')

        return chat_state

    def save_current_chat(self, messages: List, metadata: Optional[Dict] = None):
        """Save current chat state"""
        if metadata is None:
            metadata = {}

        current_branch = self.storage.get_current_branch()
        chat_id = self.storage.get_chat_id_for_branch(current_branch)

        if not chat_id:
            chat_id = self.init_branch(current_branch)

        self.storage.save_chat_state(chat_id, {
            'branch': current_branch,
            'messages': messages,
            'metadata': metadata,
            'lastSaved': datetime.now().isoformat()
        })

        print(f'✓ Saved chat state for branch "{current_branch}"')

    def create_branch(self, new_branch: str, base_branch: Optional[str] = None):
        """Create new branch with chat session"""
        base = base_branch or self.storage.get_current_branch()

        try:
            # Create Git branch
            subprocess.run(
                ['git', 'checkout', '-b', new_branch],
                cwd=self.storage.repo_root,
                check=True
            )

            # Initialize chat session
            self.init_branch(new_branch, base)

            print(f'\n✓ Created branch "{new_branch}" from "{base}"')
            print('  Chat session initialized with inherited context')

        except subprocess.CalledProcessError as e:
            print(f'Failed to create branch: {e}')

    def get_status(self) -> dict:
        """Get status information"""
        current_branch = self.storage.get_current_branch()
        chat_id = self.storage.get_chat_id_for_branch(current_branch)
        mappings = self.storage.get_branch_mapping()

        return {
            'currentBranch': current_branch,
            'currentChatId': chat_id,
            'totalBranches': len(mappings),
            'mappings': mappings
        }
