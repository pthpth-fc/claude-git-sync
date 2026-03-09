#!/usr/bin/env python3
"""
Configuration Manager for Claude Git Sync
Manages global and local configuration with precedence and validation
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ConfigManager:
    """Manage global and local configuration with precedence"""

    # Default configuration schema
    DEFAULT_CONFIG = {
        "merge": {
            "strategy": "append",
            "autoBackup": True
        },
        "archive": {
            "enabled": False,
            "maxBranchAgeDays": 90
        },
        "compression": {
            "enabled": False,
            "threshold": 1000
        },
        "search": {
            "indexEnabled": False
        },
        "output": {
            "verbose": False,
            "useColor": True,
            "pageSize": 20
        },
        "history": {
            "showTimestamps": True,
            "maxPreviewLength": 100
        }
    }

    def __init__(self, sync_dir: Path):
        """Initialize configuration manager

        Args:
            sync_dir: Path to .claude-git-sync directory
        """
        self.config_file = sync_dir / 'config.json'
        self._config = None
        self._load()

    def _load(self):
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge with defaults (user config overrides defaults)
                self._config = self._deep_merge(self.DEFAULT_CONFIG.copy(), user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")
                self._config = self.DEFAULT_CONFIG.copy()
        else:
            self._config = self.DEFAULT_CONFIG.copy()

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

    def get(self, path: str, default: Any = None) -> Any:
        """Get configuration value using dot notation

        Args:
            path: Dot-separated path (e.g., 'merge.strategy')
            default: Default value if path not found

        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, path: str, value: Any) -> bool:
        """Set configuration value using dot notation

        Args:
            path: Dot-separated path (e.g., 'merge.strategy')
            value: Value to set

        Returns:
            True if successful, False otherwise
        """
        keys = path.split('.')

        # Navigate to the parent of the target key
        target = self._config
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            elif not isinstance(target[key], dict):
                print(f"Error: Cannot set {path}, parent is not a dictionary")
                return False
            target = target[key]

        # Set the value
        target[keys[-1]] = value

        # Save to file
        return self._save()

    def _save(self) -> bool:
        """Save configuration to file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self._config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False

    def reset(self) -> bool:
        """Reset configuration to defaults

        Returns:
            True if successful, False otherwise
        """
        self._config = self.DEFAULT_CONFIG.copy()
        return self._save()

    def validate(self) -> Tuple[bool, List[str]]:
        """Validate configuration

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Validate merge strategy
        strategy = self.get('merge.strategy')
        if strategy not in ['append', 'keep', 'replace']:
            errors.append(f"Invalid merge.strategy: {strategy}. Must be 'append', 'keep', or 'replace'")

        # Validate numeric values
        max_age = self.get('archive.maxBranchAgeDays')
        if not isinstance(max_age, int) or max_age < 1:
            errors.append(f"Invalid archive.maxBranchAgeDays: {max_age}. Must be a positive integer")

        threshold = self.get('compression.threshold')
        if not isinstance(threshold, int) or threshold < 1:
            errors.append(f"Invalid compression.threshold: {threshold}. Must be a positive integer")

        page_size = self.get('output.pageSize')
        if not isinstance(page_size, int) or page_size < 1:
            errors.append(f"Invalid output.pageSize: {page_size}. Must be a positive integer")

        max_preview = self.get('history.maxPreviewLength')
        if not isinstance(max_preview, int) or max_preview < 1:
            errors.append(f"Invalid history.maxPreviewLength: {max_preview}. Must be a positive integer")

        # Validate boolean values
        for path in ['merge.autoBackup', 'archive.enabled', 'compression.enabled',
                     'search.indexEnabled', 'output.verbose', 'output.useColor',
                     'history.showTimestamps']:
            value = self.get(path)
            if not isinstance(value, bool):
                errors.append(f"Invalid {path}: {value}. Must be true or false")

        return (len(errors) == 0, errors)

    def get_all(self) -> Dict:
        """Get entire configuration

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()

    def display(self):
        """Display configuration in a readable format"""
        print("\nCurrent Configuration:")
        print("=" * 50)
        self._display_dict(self._config, indent=0)
        print("=" * 50)

    def _display_dict(self, d: Dict, indent: int = 0):
        """Recursively display dictionary

        Args:
            d: Dictionary to display
            indent: Current indentation level
        """
        for key, value in d.items():
            if isinstance(value, dict):
                print("  " * indent + f"{key}:")
                self._display_dict(value, indent + 1)
            else:
                print("  " * indent + f"{key}: {value}")
