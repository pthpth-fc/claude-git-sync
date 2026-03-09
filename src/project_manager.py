#!/usr/bin/env python3
"""
Project Manager for Claude Git Sync
Manages multiple repository installations
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ProjectInfo:
    """Information about a registered project"""
    name: str
    path: str
    branch_count: int
    total_messages: int
    last_accessed: str
    config: Dict


class ProjectManager:
    """Manage multiple repository installations"""

    def __init__(self):
        """Initialize project manager"""
        self.global_dir = Path.home() / '.claude-git-sync'
        self.global_dir.mkdir(exist_ok=True)
        self.registry_file = self.global_dir / 'projects.json'
        self._load_registry()

    def _load_registry(self):
        """Load project registry from file"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    self.registry = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load project registry: {e}")
                self.registry = {'projects': {}, 'currentProject': None}
        else:
            self.registry = {'projects': {}, 'currentProject': None}

    def _save_registry(self) -> bool:
        """Save project registry to file

        Returns:
            True if successful
        """
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.registry, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving project registry: {e}")
            return False

    def register_project(self, repo_path: str, name: Optional[str] = None) -> bool:
        """Register a new project

        Args:
            repo_path: Path to repository
            name: Optional project name (defaults to directory name)

        Returns:
            True if successful
        """
        try:
            repo_path = Path(repo_path).resolve()

            if not repo_path.exists():
                print(f"Path does not exist: {repo_path}")
                return False

            # Check if it's a git repository
            if not (repo_path / '.git').exists():
                print(f"Not a git repository: {repo_path}")
                return False

            # Check if claude-git-sync is installed
            sync_dir = repo_path / '.claude-git-sync'
            if not sync_dir.exists():
                print(f"Claude-git-sync not installed in: {repo_path}")
                print("Run setup_integration.py first")
                return False

            # Generate project name
            if not name:
                name = repo_path.name

            # Avoid duplicate names
            if name in self.registry['projects']:
                existing_path = self.registry['projects'][name]['path']
                if existing_path == str(repo_path):
                    print(f"Project already registered: {name}")
                    return True
                else:
                    # Name conflict - add suffix
                    counter = 1
                    original_name = name
                    while name in self.registry['projects']:
                        name = f"{original_name}-{counter}"
                        counter += 1
                    print(f"Name conflict resolved, using: {name}")

            # Gather project statistics
            from claude_session_manager import ClaudeSessionManager
            manager = ClaudeSessionManager(str(repo_path))

            metadata = manager.load_metadata()
            branch_count = len(metadata.get('branches', {}))
            total_messages = sum(
                info.get('messageCount', 0)
                for info in metadata.get('branches', {}).values()
            )

            # Get configuration
            config = manager.config.get_all()

            # Register project
            self.registry['projects'][name] = {
                'path': str(repo_path),
                'branchCount': branch_count,
                'totalMessages': total_messages,
                'lastAccessed': datetime.now().isoformat(),
                'config': config
            }

            self._save_registry()

            print(f"✓ Registered project: {name}")
            print(f"  Path: {repo_path}")
            print(f"  Branches: {branch_count}")
            print(f"  Messages: {total_messages}")

            return True

        except Exception as e:
            print(f"Error registering project: {e}")
            return False

    def unregister_project(self, name: str) -> bool:
        """Unregister a project

        Args:
            name: Project name

        Returns:
            True if successful
        """
        try:
            if name not in self.registry['projects']:
                print(f"Project not found: {name}")
                return False

            del self.registry['projects'][name]

            # Clear current project if it was this one
            if self.registry.get('currentProject') == name:
                self.registry['currentProject'] = None

            self._save_registry()

            print(f"✓ Unregistered project: {name}")
            return True

        except Exception as e:
            print(f"Error unregistering project: {e}")
            return False

    def list_projects(self) -> List[ProjectInfo]:
        """List all registered projects

        Returns:
            List of ProjectInfo objects
        """
        projects = []

        for name, info in self.registry.get('projects', {}).items():
            projects.append(ProjectInfo(
                name=name,
                path=info['path'],
                branch_count=info.get('branchCount', 0),
                total_messages=info.get('totalMessages', 0),
                last_accessed=info.get('lastAccessed', ''),
                config=info.get('config', {})
            ))

        return projects

    def get_project_config(self, repo_path: str) -> Dict:
        """Get merged configuration for a project

        Merges: defaults → global config → local config

        Args:
            repo_path: Path to repository

        Returns:
            Merged configuration dictionary
        """
        try:
            from config_manager import ConfigManager

            # Start with defaults
            config = ConfigManager.DEFAULT_CONFIG.copy()

            # Global config
            global_config_file = self.global_dir / 'config.json'
            if global_config_file.exists():
                try:
                    with open(global_config_file, 'r') as f:
                        global_config = json.load(f)
                    config = self._deep_merge(config, global_config)
                except Exception:
                    pass

            # Local config
            local_config_file = Path(repo_path) / '.claude-git-sync' / 'config.json'
            if local_config_file.exists():
                try:
                    with open(local_config_file, 'r') as f:
                        local_config = json.load(f)
                    config = self._deep_merge(config, local_config)
                except Exception:
                    pass

            return config

        except Exception as e:
            print(f"Error getting project config: {e}")
            return {}

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries

        Args:
            base: Base dictionary
            override: Dictionary with values to override

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def display_projects(self):
        """Display all registered projects"""
        projects = self.list_projects()

        if not projects:
            print("\nNo projects registered")
            print("Use 'project add <path>' to register a project")
            return

        current = self.registry.get('currentProject')

        print(f"\n📁 Registered Projects ({len(projects)}):")
        print("=" * 70)

        for project in sorted(projects, key=lambda p: p.last_accessed, reverse=True):
            is_current = project.name == current
            marker = "→ " if is_current else "  "

            print(f"\n{marker}{project.name}")
            print(f"    Path: {project.path}")
            print(f"    Branches: {project.branch_count}")
            print(f"    Messages: {project.total_messages}")

            if project.last_accessed:
                try:
                    dt = datetime.fromisoformat(project.last_accessed)
                    time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                    print(f"    Last accessed: {time_str}")
                except:
                    pass

        print("\n" + "=" * 70)

    def show_project_info(self, name: str) -> bool:
        """Show detailed information about a project

        Args:
            name: Project name

        Returns:
            True if successful
        """
        if name not in self.registry['projects']:
            print(f"Project not found: {name}")
            return False

        info = self.registry['projects'][name]
        repo_path = Path(info['path'])

        print(f"\n📋 Project: {name}")
        print("=" * 70)
        print(f"Path: {repo_path}")

        # Check if path still exists
        if not repo_path.exists():
            print("⚠️  WARNING: Path no longer exists!")

        print(f"\nStatistics:")
        print(f"  Branches: {info.get('branchCount', 0)}")
        print(f"  Total messages: {info.get('totalMessages', 0)}")

        if info.get('lastAccessed'):
            try:
                dt = datetime.fromisoformat(info['lastAccessed'])
                time_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                print(f"  Last accessed: {time_str}")
            except:
                pass

        # Show configuration
        if info.get('config'):
            print(f"\nConfiguration:")
            self._display_config(info['config'], indent=2)

        print("=" * 70)
        return True

    def _display_config(self, config: Dict, indent: int = 0):
        """Recursively display configuration

        Args:
            config: Configuration dictionary
            indent: Indentation level
        """
        for key, value in config.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                self._display_config(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")
